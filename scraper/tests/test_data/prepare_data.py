# TODO: Make everything configurable (year, raceId)

import json
from scraper import Parser
import requests
from pathlib import Path
import argparse

parser = Parser()

DATA_PATH = "tests/test_data/html"
CONFIG_PATH = "tests/test_data/config"
YEAR = 2023

def writeFile(path: str, data: str, encoding: str) -> None:
    with open(path, "w", encoding=encoding) as file:
        file.write(data)
        
def saveHtml(url: str, path: str) -> tuple[str, str]:
    html = requests.get(url)
    writeFile(path, html.text, html.encoding)
    return str(Path(path)), html.encoding

def prepareSchedulePage(dataPath: str, year: int) -> tuple[str, str]:
    url = parser.YEAR_SCHEDULE_URL.format(year=year)
    return saveHtml(url, f"{dataPath}/{year}_schedule.html")

def prepareDriverStandingsPage(dataPath: str, year: int) -> tuple[str, str]:
    url = parser.DRIVERS_STANDINGS_URL.format(year=year)
    return saveHtml(url, f"{dataPath}/{year}_driver_standings.html")

def prepareConstructorStandingsPage(dataPath: str, year: int) -> tuple[str, str]:
    url = parser.CONSTRUCTORS_STANDINGS_URL.format(year=year)
    return saveHtml(url, f"{dataPath}/{year}_constructor_standings.html")

def prepareRegularRaceWeekendPage(dataPath: str) -> tuple[str, str]:
    url = "https://www.formula1.com/en/racing/2023/saudi-arabia"
    return saveHtml(url, f"{dataPath}/2023_regular_weekend_ksa.html")
    
def prepareSprintRaceWeekendPage(dataPath: str) -> tuple[str, str]:
    url = "https://www.formula1.com/en/racing/2023/brazil"
    return saveHtml(url, f"{dataPath}/2023_sprint_weekend_br.html")

def prepareCircuitPage(dataPath: str) -> tuple[str, str]:
    url = "https://www.formula1.com/en/racing/2023/brazil/circuit"
    return saveHtml(url, f"{dataPath}/2023_circuit_br.html")

def prepareRaceResultPage(dataPath: str) -> tuple[str, str]:
    url = "https://www.formula1.com/en/results/2023/races/1224/brazil/race-result"
    return saveHtml(url, f"{dataPath}/2023_race_result_br.html")

def prepareQualifyingResultPage(dataPath: str) -> tuple[str, str]:
    url = "https://www.formula1.com/en/results/2023/races/1224/brazil/qualifying"
    return saveHtml(url, f"{dataPath}/2023_qualifying_result_br.html")

def preparePracticeResultPage(dataPath: str) -> tuple[str, str]:
    url = "https://www.formula1.com/en/results/2023/races/1224/brazil/practice/1"
    return saveHtml(url, f"{dataPath}/2023_practice_result_br.html")

def writeConfig(config: dict[str, str], path: str, year: int):
    with open(f"{path}/{year}_config.json", "w") as f:
        json.dump(config, f, indent=4)
        
def main(year: int, configPath: str, dataPath: str):
    config =  {
        "year": year,
        "schedule_page": prepareSchedulePage(dataPath, year),
        "driver_standings_page": prepareDriverStandingsPage(dataPath, year),
        "constructor_standings_page": prepareConstructorStandingsPage(dataPath, year),
        "regular_weekend_page": prepareRegularRaceWeekendPage(dataPath),
        "sprint_weekend_page": prepareSprintRaceWeekendPage(dataPath),
        "circuit_page": prepareCircuitPage(dataPath),
        "practice_result_page": preparePracticeResultPage(dataPath),
        "qualifying_result_page": prepareQualifyingResultPage(dataPath),
        "race_result_page": prepareRaceResultPage(dataPath)
    }
    writeConfig(config, configPath, year)
    
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-d", "--data-path", type=Path, default=DATA_PATH)
    argparser.add_argument("-c", "--config-path", type=Path, default=CONFIG_PATH)
    argparser.add_argument("-y", "--year", type=int, default=YEAR)
    args = argparser.parse_args()
    
    main(args.year, args.config_path, args.data_path)
