import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
from typing import *
import time
import asyncio
from models import Race
from dataclasses import asdict

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
    
    
    async def getCircuit(self, raceUrl: str) -> Dict[str, str]:
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
        
        return circuit
    
    
    def __parseEvent(self, raceId: str, containerDiv: BeautifulSoup) -> dict[str, str]:
        title = containerDiv.find('p', class_='f1-timetable--title')
        time = containerDiv.parent['data-start-time'].split("T")
        gmtOff = containerDiv.parent['data-gmt-offset']
        
        event = {
            "raceId": raceId,
            "title": title.string,
            "date": time[0],
            "time": time[1],
            "gmtOffset": gmtOff,
            "resultLink": None
        }
        
        resultLinkA = containerDiv.find('a')
        
        if resultLinkA:
            resultLink = resultLinkA['href']
            event["resultLink"] = resultLink
            
        return event
    
    def __parseTable(self, table: BeautifulSoup, propMap: dict[str, str] = {}, initial: dict[str, str] = {}) -> List[dict[str, str]]:
        infos = [ele.lower() for ele in table.thead.tr.stripped_strings]
        
        tableData: List[dict[str, str]] = []
        for child in table.tbody.children:
            if child == "\n":
                continue
            
            rowData = []
            for ch in child.children:
                joined = " ".join(ch.stripped_strings)
                if joined:
                    rowData.append(joined)
            
            while len(rowData) < len(infos):
                end = rowData.pop()
                rowData.append("")
                rowData.append(end)
                
            row = initial.copy()
            for ind, res in enumerate(rowData):
                row[self.__propMapper(infos[ind].lower(), propMap)] = res
                
            tableData.append(row)
            
        return tableData
        
    
    async def getEventResults(self, url : str, eventId: str) -> List[Dict[str, str]]:
        soup = await self.__getSoup(url)
        
        title = soup.find('h1', class_='ResultsArchiveTitle').string.split("-")[-1].strip()
        resultTable = soup.find('table', class_='resultsarchive-table')
        
        propMap = { 
            "pos": "position", "driver": "driverName", "car": "constructorName", "no": "driverNumber",
            "time/retired": "time", "pts": "points"
        }
        
        results = self.__parseTable(resultTable, propMap, initial={"eventId": eventId, "eventTitle": title})
        
        return results
    
    def __isTrackMap(self, alt: str) -> bool:
        return alt and ('carbon.png' in alt or 'carbon_original.png' in alt.lower())
    
    
    def __getYear(self, url: str) -> int:
        splitUrl = url.split("/")
        return int(splitUrl[splitUrl.index("racing") + 1])
    
    
    async def getRace(self, url: str, round_: int) -> Dict[str, Any]:
        soup = await self.__getSoup(url)
        
        year = self.__getYear(url)
        raceLocation = soup.find('h1', class_='race-location').contents[0]
        raceName = soup.find('h2', class_='f1--s').string
        trackMapImg = soup.find('img', alt=self.__isTrackMap)['data-src']
        raceId = Race.formatRaceId(year, round_)

        upcoming = soup.find_all('div', class_='upcoming')
        completed = soup.find_all('div', class_='completed')
        
        events = [self.__parseEvent(raceId ,eventDiv) for eventDiv in upcoming + completed]
        circuit = await self.getCircuit(url)
        
        race = {
            "year": year,
            "round_": round_,
            "name": raceName,
            "location": raceLocation,
            "trackMap": trackMapImg,
            "circuit": circuit,
            "events": events
        }
        
        return race
    
    
    async def __getStandings(self, url: str, propMap: dict[str, str] = {}) -> List[dict[str, str]]:
        soup = await self.__getSoup(url)
        
        table = soup.find('table', class_='resultsarchive-table')
      
        standings = self.__parseTable(table, propMap)
        return standings
    
    
    async def getDriverStandings(self, year: int) -> List[Dict[str, str]]:
        url = self.DRIVERS_STANDINGS_URL.format(year=year)
        propMap = { "pos": "position", "driver": "driverName", "car": "constructorName", "pts": "points" }
        
        driverStandings = await self.__getStandings(url, propMap)
        
        return driverStandings
    
    
    async def getConstructorStandings(self, year: int) -> List[Dict[str, str]]:
        url = self.CONSTRUCTORS_STANDINGS_URL.format(year=year)
        propMap = { "pos": "position", "team": "constructorName", "pts": "points" }
        
        constructorStandings = await self.__getStandings(url, propMap)
        
        return constructorStandings
        