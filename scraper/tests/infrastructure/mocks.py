from enum import Enum
import re
from pathlib import Path
import os
import json

"""
EXAMPLES

race weekend:           https://www.formula1.com/en/racing/2024/brazil
year schedule:          https://www.formula1.com/en/racing/2024
constructor standings:  https://www.formula1.com/en/results/2024/team
driver standings:       https://www.formula1.com/en/results/2024/drivers
circuit:                https://www.formula1.com/en/racing/2023/brazil/circuit
race result:            https://www.formula1.com/en/results/2023/races/1224/brazil/race-result
practice result:        https://www.formula1.com/en/results/2023/races/1224/brazil/practice/1
qualifying result:      https://www.formula1.com/en/results/2023/races/1224/brazil/qualifying
"""
        
BASE_URL = "https://www.formula1.com/en/"


class RequestType(Enum):
    YEAR_SCHEDULE = "YR_SCH"
    DRIVER_STANDINGS = "DRI_STNDGS"
    CONSTRUCTROR_STANDINGS = "CON_STNDGS"
    RACE_WEEKEND = "RACE_WKND"
    CIRCUIT = "CRCT"
    PRACTICE_RESULT = "PRA_RES"
    QUALIFYING_RESULT = "QUALI_RES"
    RACE_RESULT = "RACE_RES"
    
    @staticmethod
    def parseType(url: str) -> "RequestType":
        path = re.sub(BASE_URL, "", url)

        if re.fullmatch(r"^racing/\d{4}/[a-zA-Z-]+/?$", path):
            return RequestType.RACE_WEEKEND
        if re.fullmatch(r"^results/\d{4}/team/?$", path):
            return RequestType.CONSTRUCTROR_STANDINGS
        if re.fullmatch(r"^results/\d{4}/drivers/?$", path):
            return RequestType.DRIVER_STANDINGS
        if re.fullmatch(r"^racing/\d{4}/?$", path):
            return RequestType.YEAR_SCHEDULE
        if re.fullmatch(r"^racing/\d{4}/[a-zA-Z-]+/circuit/?$", path):
            return RequestType.CIRCUIT
        if re.fullmatch(r"^results/\d{4}/races/\d+/[a-zA-Z-]+/practice/\d+/?$", path):
            return RequestType.PRACTICE_RESULT
        if re.fullmatch(r"^results/\d{4}/races/\d+/[a-zA-Z-]+/(sprint-|)qualifying/?$", path):
            return RequestType.QUALIFYING_RESULT
        if re.fullmatch(r"^results/\d{4}/races/\d+/[a-zA-Z-]+/(race|sprint)-result(s|)/?$", path):
            return RequestType.RACE_RESULT

        raise Exception(f"can't parse request type for url: {url}")


class MockConfig:
    def __init__(self, config: dict[str, tuple[str, str]]):
        self.year = config["year"]
        self.schedulePage = config["schedule_page"]
        self.constructorStandingsPage = config["constructor_standings_page"]
        self.driverStandingsPage = config["driver_standings_page"]
        self.regularWeekendPage = config["regular_weekend_page"]
        self.sprintWeekendPage = config["sprint_weekend_page"]
        self.circuitPage = config["circuit_page"]
        self.raceResultPage = config["race_result_page"]
        self.qualifyingResultPage = config["qualifying_result_page"]
        self.practiceResultPage = config["practice_result_page"]
            

class MockResponse:
    def __init__(self, text: str, encoding: str):
        self.text = text
        self.encoding = encoding
        
    @staticmethod
    def fromFile(path: str | Path, encoding: str = "utf-8"):
        with open(str(path), encoding=encoding) as f:
            return MockResponse(f.read(), encoding)


class MockRequests:
    def __init__(self, config: os.PathLike | str | dict[str, tuple[str, str]]):
        if isinstance(config, str):
            config = Path(config)
        if isinstance(config, os.PathLike):
            config = self.__read_config(config)
        self.config = MockConfig(config)
        
        self.typeMap = {
            RequestType.YEAR_SCHEDULE: MockResponse.fromFile(*self.config.schedulePage),
            RequestType.DRIVER_STANDINGS: MockResponse.fromFile(*self.config.driverStandingsPage),
            RequestType.CONSTRUCTROR_STANDINGS: MockResponse.fromFile(*self.config.constructorStandingsPage),
            RequestType.RACE_WEEKEND: MockResponse.fromFile(*self.config.regularWeekendPage),
            RequestType.CIRCUIT: MockResponse.fromFile(*self.config.circuitPage),
            RequestType.RACE_RESULT: MockResponse.fromFile(*self.config.raceResultPage),
            RequestType.QUALIFYING_RESULT: MockResponse.fromFile(*self.config.qualifyingResultPage),
            RequestType.PRACTICE_RESULT: MockResponse.fromFile(*self.config.practiceResultPage)
        } 
            
    def __read_config(self, path: os.PathLike) -> dict[str, tuple[str, str]]:
        with open(str(path)) as f:
            return json.load(f)

    def get(self, url: str, headers: dict[str, any] = None) -> MockResponse:
        reqType = RequestType.parseType(url)
        
        return self.typeMap[reqType]
    
    def getSprintRace(self) -> MockResponse:
        return MockResponse(*self.config.sprintWeekendPage)
