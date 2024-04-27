from dataclasses import dataclass
from .BaseModel import BaseModel
from .Driver import Driver
from .Constructor import Constructor

@dataclass
class Standings(BaseModel):
    year: int
    position: int
    points: int
    
    @staticmethod
    def fromDict(**kwargs):
        if kwargs.get("driverName"):
            return DriverStandings(**kwargs)
        if kwargs.get("constructorName"):
            return ConstructorStandings(**kwargs)
        else:
            raise Exception("Invalid type")

@dataclass
class DriverStandings(Standings):
    driverId: str
    constructorId: str
    nationality: str
    
@dataclass
class ConstructorStandings(Standings):
    constructorId: str