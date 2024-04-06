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
        if kwargs["driverId"]:
            return DriverStandings(**kwargs)
        if kwargs["constructorName"]:
            return ConstructorStandings(**kwargs)
        else:
            raise Exception("Invalid type")

@dataclass
class DriverStandings(Standings):
    driverId: str
    driverName: str
    constructorName: str
    driver: Driver
    
    
@dataclass
class ConstructorStandings(Standings):
    constructorId: str
    constructorName: str
    constructor: Constructor