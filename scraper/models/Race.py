from dataclasses import dataclass
from .RaceEvent import RaceEvent
from .Circuit import Circuit
from typing import List
from .BaseModel import BaseModel

@dataclass
class Race(BaseModel):
    f1Id: str
    year: int
    round_: int
    name: str
    location: str
    trackMap: str
    circuitId:str
    id_: str = None
    
    def __post_init__(self):
        self.id_ = self.formatRaceId(self.year, self.round_)
        
    def setCircuit(self, circuitId: str) -> None:
        self.circuitId = circuitId
        
    # def __str__(self):
    #     # return f"{self.name} {self.year}"
    #     pass
    
    @staticmethod
    def formatRaceId(year: int, round_: int) -> str:
        return f"{year}_{round_}"
    
    @staticmethod
    def fromDict(**kwargs) -> 'Race':
        return Race(**kwargs)