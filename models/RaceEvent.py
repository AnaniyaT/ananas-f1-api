from dataclasses import dataclass
from models.Result import Result
from typing import List

@dataclass
class RaceEvent:
    raceId: str
    title: str
    date: str
    time: str
    gmtOffset: str
    results: List[Result] = None
    
    def __post_init__(self):
        self.id = f"{self.raceId}_{self.title}"
        if self.results is None:
            self.results = []
            
    def addResult(self, result: Result) -> None:
        self.results.append(result)
    
    def addResults(self, results: List[Result]) -> None:
        self.results.extend(results)
