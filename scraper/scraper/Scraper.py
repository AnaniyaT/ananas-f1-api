import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from db import Database
from models import Circuit, Driver, EventType, Race, RaceEvent, Result, DriverStandings
from models import Constructor, ConstructorStandings
from .Parser import Parser
from typing import Any, List, Dict, Tuple
import asyncio

from utils import Utils

class Scraper:
    """
    Object that scrapes the data from the F1 website and stores it in the database
    """
    parser = Parser()
    
    def __init__(self, dbPath: str = None) -> None:
        self.db = Database(path=dbPath)
    
    def __raceDictDigest(self, raceDict: Dict[str, Any]) -> Tuple[Race, List[RaceEvent], Circuit]:
        circuit = raceDict.pop("circuit")
        events = raceDict.pop("events")
        
        circuit["numberOfLaps"] = int(circuit["numberOfLaps"])
        circuit["length"] = float(circuit["length"].split()[0])
        circuit["raceDistance"] = float(circuit["raceDistance"].split()[0])
        
        circuit = Circuit.fromDict(**circuit)
        raceDict["circuitId"] = circuit.id_
        race = Race.fromDict(**raceDict)
        
        for idx, event in enumerate(events):
            event["type_"] = EventType.getType(event["title"]).value
            event["raceId"] = race.id_
            event.pop("resultLink")
            events[idx] = RaceEvent(**event)

        return race, events, circuit
    
    
    async def saveAllRaces(self, year: int) -> None:
        """
        Scrapes all Race, RaceEvent and Circuit data for a given year and stores it in the database
        """
        urls = await self.parser.getRaceUrls(year)
        
        tasks = [self.parser.getRace(url, idx + 1) for idx, url in enumerate(urls)]
            
        racesDicts = await asyncio.gather(*tasks)
        
        races, events, circuits = [], [], []
        for raceDict in racesDicts:
            r, e, c = self.__raceDictDigest(raceDict)
            races.append(r)
            events.extend(e)
            circuits.append(c)
            
        self.db.circuits.insertOrUpdateMany(circuits)
        self.db.races.insertOrUpdateMany(races)
        self.db.events.insertOrUpdateMany(events)
        
        self.db.commit()
        
        
    
    async def saveEventResults(self, url: str, eventId: str) -> None:
        """
        Scrapes the results of a given event and stores it in the database
        """
        parsedResults = await self.parser.getEventResults(url, eventId)
        
        results = []
        for result in parsedResults:
            result.pop("eventTitle")
            driverName = " ".join(result.pop("driverName").split()[:-1])
            result["driverId"] = Driver.getDriverId(driverName)
            result["constructorId"] = Constructor.getConstructorId(result.pop("constructorName"))
            results.append(Result.fromDict(**result))
            
        allConstructorsExistInDb = all([
            self.db.constructors.exists(id_=result.constructorId) for result in results
        ])
        
        if not allConstructorsExistInDb:
            await self.saveConstructorsAndStandings(RaceEvent.getEventYear(eventId))
            
        allDriversExistInDb = all([
            self.db.drivers.exists(id_=result.driverId) for result in results
        ])
        
        if not allDriversExistInDb:
            await self.saveDriversAndStandings(RaceEvent.getEventYear(eventId))
        
        self.db.results.insertOrUpdateMany(results)
        self.db.commit()
    
    
    async def saveRaceResults(self, year: int, round_: int) -> None:
        raceUrls = await self.parser.getRaceUrls(year)
        raceUrl = raceUrls[round_ - 1]
        raceId = Race.formatRaceId(year, round_)
        
        parsedEvents = (await self.parser.getRace(raceUrl, round_))["events"]
        tasks = []
        
        for event in parsedEvents:
            eventId = RaceEvent.formatEventId(raceId, event["title"])
            resultLink = event["resultLink"]
            
            # If it's a future event or we already have the results for the event
            if not resultLink or self.db.results.exists(eventId=eventId):
                continue
            
            tasks.append(self.saveEventResults(resultLink, eventId))
            
        await asyncio.gather(*tasks)
        
    
    async def saveAllResults(self, year: int) -> None:
        raceUrls = await self.parser.getRaceUrls(year)
        
        getRounds = []
        for round_ in range(1, len(raceUrls) + 1):
            eventId = f"{year}_{round_}_RACE"
            if not self.db.results.exists(eventId=eventId):
                getRounds.append(round_)
                
        tasks = [self.saveRaceResults(year, round_) for round_ in getRounds]
        await asyncio.gather(*tasks)
        
            
    async def saveRace(self, year: int, round_: int) -> None:
        urls = await self.parser.getRaceUrls(year)
        
        raceDict = await self.parser.getRace(urls[round_ - 1], round_)
        
        race, events, circuit = self.__raceDictDigest(raceDict)
        
        self.db.circuits.insertOrUpdate(circuit)
        self.db.races.insertOrUpdate(race)
        self.db.events.insertOrUpdateMany(events)
        
        self.db.commit()
    
    
    async def saveDriversAndStandings(self, year: int) -> List[DriverStandings]:
        standingsDicts = await self.parser.getDriverStandings(year)
        
        allConstructorsExistInDb = all([
            self.db.constructors.exists(name=standingDict["constructorName"]) for standingDict in standingsDicts
        ])
        
        if not allConstructorsExistInDb:
            await self.saveConstructorsAndStandings(year)
        
        drivers = [
            Driver(
                name=Utils.getNameAndShortName(standingDict["driverName"])[0],
                shortName=Utils.getNameAndShortName(standingDict["driverName"])[1],
                nationality=standingDict["nationality"],
                constructorId=Constructor.getConstructorId(standingDict["constructorName"])
            )
            
            for standingDict in standingsDicts
        ]
        
        standings = [
            DriverStandings(
                year=year,
                position=standingDict["position"],
                points=standingDict["points"],
                driverId=Driver.getDriverId(Utils.getNameAndShortName(standingDict["driverName"])[0]),
                constructorId=Constructor.getConstructorId(standingDict["constructorName"]),
            )
            
            for standingDict in standingsDicts
        ]
        
        self.db.drivers.insertOrUpdateMany(drivers)
        self.db.driverStandings.insertOrUpdateMany(standings)
        
        self.db.commit()
    
    
    async def saveConstructorsAndStandings(self, year: int) -> List[ConstructorStandings]:
        standingsDicts = await self.parser.getConstructorStandings(year)
        
        constructors = [
            Constructor(
                name=standing["constructorName"],
            )
            
            for standing in standingsDicts
        ]
        
        standings = [
            ConstructorStandings(
                year=year,
                position=standing["position"], 
                points=standing["points"],
                constructorId=Constructor.getConstructorId(standing["constructorName"])
            )
            
            for standing in standingsDicts
        ]
        
        self.db.constructors.insertOrUpdateMany(constructors)
        self.db.constructorStandings.insertOrUpdateMany(standings)
        
        self.db.commit()
        