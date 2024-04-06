from dataclasses import dataclass

from .BaseModel import BaseModel
from .EventType import EventType
from .Result import Result
from typing import List

@dataclass
class RaceEvent(BaseModel):
    raceId: str
    title: str
    date: str
    type_: EventType
    time: str
    gmtOffset: str
    results: List[Result] = None
    id: str = None
    
    def __post_init__(self):
        self.id = f"{self.raceId}_{self.title}".replace(" ", "_").upper()
        if self.results is None:
            self.results = []
            
    def addResult(self, result: Result) -> None:
        self.results.append(result)
    
    def addResults(self, results: List[Result]) -> None:
        self.results.extend(results)
