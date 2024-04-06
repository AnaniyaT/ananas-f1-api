from dataclasses import dataclass
from .BaseModel import BaseModel

@dataclass
class Circuit(BaseModel):
    name: str
    numberOfLaps: int
    length: float
    raceDistance: float
    lapRecord: str
    firstGrandPrix: str
    id: str = None
    
    def __str__(self):
        return self.name
    
    def __post_init__(self):
        self.id = self.name
    
    @staticmethod
    def fromDict(**kwargs):
        return Circuit(**kwargs)

    