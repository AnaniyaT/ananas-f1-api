import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import re
import requests
from bs4 import BeautifulSoup
from typing import *
import time
import asyncio


# Where all the dirty work is done, Parser really took one for the team here
class Parser:
    BASE_URL = "https://www.formula1.com"
    DRIVERS_STANDINGS_URL = BASE_URL + "/en/results/{year}/drivers"
    CONSTRUCTORS_STANDINGS_URL = BASE_URL + "/en/results/{year}/team"
    YEAR_SCHEDULE_URL = BASE_URL + "/en/racing/{year}"

    def __camelCase(self, string: str) -> str:
        if not string or not string.strip():
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        }
        html = await asyncio.to_thread(requests.get, url, headers=headers)
        htmlText = html.text.encode(html.encoding).decode("utf-8")
        soup = BeautifulSoup(htmlText, "html.parser")

        return soup

    async def getRaceUrls(self, year: int, use_cache: bool = True) -> List[str]:
        # caching shenanigans
        cache_directory = Path(__file__).parent / "__cache__" / f"{year}_urls.json"

        if cache_directory.exists() and use_cache:
            with open(cache_directory, "r") as file:
                cache_data = json.load(file)
                last_updated = cache_data["last_updated"]
                urls = cache_data["data"]

                if time.time() - last_updated < 3600 * 24 * 7 and urls:  # 1 week
                    print("cache hit")
                    return urls

        else:
            cache_directory.parent.mkdir(parents=True, exist_ok=True)

        # actual scraping

        url = self.YEAR_SCHEDULE_URL.format(year=year)
        soup = await self.__getSoup(url)

        wrapperDiv = soup.find("div", class_="f1-inner-wrapper")

        raceUrlAs = wrapperDiv.find_all(
            "a", href=re.compile(r"^/en/racing/\d{4}/[\w-]+$")
        )
        raceUrls = list(map(lambda x: self.BASE_URL + x["href"], raceUrlAs))

        filteredUrls = [url for url in raceUrls if not "pre-season" in url.lower()]

        # more caching shenanigans
        if use_cache:
            with open(cache_directory, "w") as file:
                json.dump({"last_updated": time.time(), "data": filteredUrls}, file)

        return filteredUrls

    async def getCircuit(self, raceUrl: str) -> Dict[str, str]:
        url = raceUrl + "/circuit"

        soup = await self.__getSoup(url)
        trackName = soup.find("h2", class_="f1-heading").string

        stats = soup.find_all("span", class_="f1-text")

        circuit = {"name": trackName}

        propMap = {"circuitLength": "length", trackName: "name"}

        for stat in stats:
            if not stat.string:
                continue
            val = stat.next_sibling
            if not val:
                continue
            val = " ".join(val.stripped_strings)
            circuit[self.__propMapper(stat.string, propMap)] = val

        return circuit

    def __parseEvents(self, events: list[dict[str, any]]) -> dict[str, str]:
        events = [
            {
                "title": event["name"].split(" - ")[0],
                "startDate": event["startDate"],
                "endDate": event["endDate"],
                "resultLink": None
            } for event in events
        ]

        return events

    def __parseTable(
        self,
        table: BeautifulSoup,
        propMap: dict[str, str] = {},
        initial: dict[str, str] = {},
    ) -> List[dict[str, str]]:
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

    async def getEventResults(self, url: str, eventId: str) -> List[Dict[str, str]]:
        soup = await self.__getSoup(url)

        title = soup.find("h1").string.split("-")[-1].strip()
        if title.lower().endswith("result"):
            title = title.split()[0]
            
        resultTable = soup.find("table")

        propMap = {
            "pos": "position",
            "driver": "driverName",
            "car": "constructorName",
            "no": "driverNumber",
            "time/retired": "time",
            "pts": "points",
        }

        results = self.__parseTable(
            resultTable, propMap, initial={"eventId": eventId, "eventTitle": title}
        )

        return results

    def __isTrackMap(self, attr: str) -> bool:
        return attr and ("carbon" in attr or "carbon" in attr.lower())

    def __getYear(self, url: str) -> int:
        splitUrl = url.split("/")
        return int(splitUrl[splitUrl.index("racing") + 1])
    
    def __parseEventResultLinks(self, soup: BeautifulSoup) -> tuple[list[str], str]:
        def isResultLink(link: str) -> bool:
            link = link.removeprefix("https://www.formula1.com/en/")
            return bool(re.fullmatch(r'results(?:\.html)?/\d{4}/races/\d+/-?[\w-]+/-?[\w-]+(?:\.html)?/?', link))

        links = soup.findAll("a", href=isResultLink)
        links = [tag["href"] for tag in links]

        return links, links[0].removeprefix("https://www.formula1.com/en/").split("/")[3]
    
    async def getRace(self, url: str, round_: int) -> Dict[str, Any]:
        soup = await self.__getSoup(url)
        year = self.__getYear(url)
        
        json_ld_tags = soup.findAll("script", type="application/ld+json")
        raceData = {}
        for tag in json_ld_tags:
            jsonData = json.loads(tag.string)
            if jsonData.get("@type") == "SportsEvent":
                raceData = jsonData
                break
            
        raceLocation = raceData["location"]["address"]
        raceName = raceData["name"]
        trackMapImg = soup.find("img", src=self.__isTrackMap)["src"]

        events = self.__parseEvents(raceData["subEvent"])
        resultLinks, f1RaceId = self.__parseEventResultLinks(soup)
        
        for idx, event in enumerate(events):
            event["resultLink"] = resultLinks[-1-idx]
        
        circuit = await self.getCircuit(url)

        race = {
            "f1Id": f1RaceId,
            "year": year,
            "round_": round_,
            "name": raceName,
            "location": raceLocation,
            "trackMap": trackMapImg,
            "circuit": circuit,
            "events": events,
        }

        return race

    async def __getStandings(
        self, url: str, propMap: dict[str, str] = {}
    ) -> List[dict[str, str]]:
        soup = await self.__getSoup(url)

        table = soup.find("table")

        standings = self.__parseTable(table, propMap)
        return standings

    async def getDriverStandings(self, year: int) -> List[Dict[str, str]]:
        url = self.DRIVERS_STANDINGS_URL.format(year=year)
        propMap = {
            "pos": "position",
            "driver": "driverName",
            "car": "constructorName",
            "pts": "points",
        }

        driverStandings = await self.__getStandings(url, propMap)

        return driverStandings

    async def getConstructorStandings(self, year: int) -> List[Dict[str, str]]:
        url = self.CONSTRUCTORS_STANDINGS_URL.format(year=year)
        propMap = {"pos": "position", "team": "constructorName", "pts": "points"}

        constructorStandings = await self.__getStandings(url, propMap)

        return constructorStandings
