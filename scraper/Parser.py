import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
from typing import *
import time
import asyncio
from models import BaseModel, Circuit, RaceEvent, Result
from models.EventType import EventType
from models.Race import Race
from dataclasses import asdict

async def print_when_done(function):
    async def wrapper():
        await function()
        print("Done")
        
    return wrapper

class Parser:
    BASE_URL = "https://www.formula1.com"
    DRIVERS_STANDINGS_URL = BASE_URL + "/en/results.html/{year}/drivers.html"
    CONSTRUCTORS_STANDINGS_URL = BASE_URL + "/en/results.html/{year}/team.html"
    YEAR_SCHEDULE_URL = BASE_URL + "/en/racing/{year}.html"
    
    
    def __camelCase(self, string: str) -> str:
        if not string:
            return ""
        
        split = string.split()
        res = [split[0].lower()]
        res.extend([word.capitalize() for word in split[1:]])
        
        return "".join(res)
    
    
    def __propMapper(self, stat: str, mapper: dict[str, str]) -> str:
        """Maps the stat to the correct property name in the class

        Args:
            stat (str): the stat to map
            mapper (dict[str, str]): the mapper to use

        Returns:
            str: the mapped property name
        """
        if self.__camelCase(stat) in mapper:
            return mapper[self.__camelCase(stat)]
        
        return self.__camelCase(stat)
    
    
    async def __getSoup(self, url: str) -> BeautifulSoup:
        html = await asyncio.to_thread(requests.get, url)
        htmlText = html.text
        soup = BeautifulSoup(htmlText, 'html.parser')
        
        return soup
    
    
    async def getRaceUrls(self, year: int) -> List[str]:
        url = self.YEAR_SCHEDULE_URL.format(year=year)
        soup = await self.__getSoup(url)
        
        raceUrlAs = soup.find_all('a', class_='event-item-wrapper event-item-link')
        raceUrls = list(map(lambda x: self.BASE_URL + x['href'], raceUrlAs))
        
        return raceUrls
    
    
    async def getCircuit(self, raceUrl: str) -> Circuit:
        splitUrl = raceUrl.split(".")
        splitUrl.pop()
        url = ".".join(splitUrl) + "/Circuit.html"
        
        soup = await self.__getSoup(url)
        flag = soup.find('span', class_='f1-flag--wrapper')
        trackName = flag.next_sibling.next_sibling.string
        
        stats = soup.find_all('div', class_='f1-stat')
        
        circuit = {"name": trackName}
        
        propMap = { "circuitLength": "length", trackName: "name" }
        
        for stat in stats:
            contents = [content for content in stat.stripped_strings]
            circuit[self.__propMapper(contents[0], propMap)] = " ".join(contents[1:])
        
        return Circuit.fromDict(**circuit)
    
    
    async def getEvent(self, raceId: str, containerDiv: BeautifulSoup, completed: bool = False, getReults: bool = True) -> RaceEvent:
        title = containerDiv.find('p', class_='f1-timetable--title')
        time = containerDiv.parent['data-start-time'].split("T")
        gmtOff = containerDiv.parent['data-gmt-offset']
        
        event = RaceEvent(
            raceId=raceId,
            title=title.string,
            date=time[0],
            time=time[1],
            gmtOffset=gmtOff,
            type_=EventType.getType(title.string)
        )
        
        if completed and getReults:
            resultLink = containerDiv.find('a')['href']
            results = await self.getEventResults(resultLink, event.id)
            event.addResults(results)
            
        return event
    
    
    async def getEventResults(self, url : str, eventId: str) -> List[Result]:
        resultArr = []
        soup = await self.__getSoup(url)
        
        title = soup.find('h1', class_='ResultsArchiveTitle').string.split("-")[-1].strip()
        type_ = EventType.getType(title)
        resultTable = soup.find('table', class_='resultsarchive-table')
        
        infos = [ele for ele in resultTable.thead.tr.stripped_strings]
        
        propMap = { 
            "pos": "position", "driver": "driverName", "car": "constructorName", "no": "driverId",
            "time/retired": "time", "pts": "points"
        }
        for child in resultTable.tbody.children:
            if child == "\n":
                continue
            
            data = []
            for ch in child.children:
                joined = " ".join(ch.stripped_strings)
                if joined:
                    data.append(joined)
            
            while len(data) < len(infos):
                end = data.pop()
                data.append("")
                data.append(end)
                
            result = { "type_": type_, "eventId": eventId }
            for ind, res in enumerate(data):
                result[self.__propMapper(infos[ind].lower(), propMap)] = res
                
            result["driverName"] = " ".join(result["driverName"].split()[:-1])
                
            resultArr.append(Result.fromDict(**result))
        
        return resultArr
    
    def __isTrackMap(self, alt: str) -> bool:
        return alt and ('carbon.png' in alt or 'carbon_original.png' in alt.lower())
    
    
    def __getYear(self, url: str) -> int:
        splitUrl = url.split("/")
        return int(splitUrl[splitUrl.index("racing") + 1])
    
    
    async def getRace(self, url: str, round_: int, getResults: bool = True) -> Race:
        soup = await self.__getSoup(url)
        
        year = self.__getYear(url)
        raceLocation = soup.find('h1', class_='race-location').contents[0]
        raceName = soup.find('h2', class_='f1--s').string
        trackMapImg = soup.find('img', alt=self.__isTrackMap)['data-src']
        
        race = Race(year, round_, raceName, raceLocation, trackMapImg)

        upcoming = soup.find_all('div', class_='upcoming')
        completed = soup.find_all('div', class_='completed')
            
        tasks = [self.getEvent(race.id, eventDiv) for eventDiv in upcoming]
        tasks += [self.getEvent(race.id, eventDiv, completed=True, getReults=getResults) for eventDiv in completed]
        tasks.append(self.getCircuit(url))
        
        events = await asyncio.gather(*tasks)
        
        race.addEvents(events[:-1])
        
        circuit = events[-1]
        race.setCircuit(circuit)
        
        return race
    