from dataclasses import dataclass
from models.Driver import Driver
from models.Constructor import Constructor

@dataclass
class Standings:
    position: int
    points: int

@dataclass
class DriverStandings(Standings):
    driverId: str
    driverName: str
    constructorName: str
    driver: Driver
    
    
@dataclass
class ConstructorStandings(Standings):
    constructorName: str
    constructor: Constructor