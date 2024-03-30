from dataclasses import dataclass
from models.Constructor import Constructor

@dataclass
class Driver:
    driverId: str
    driverName: str
    constructorName: str
    constructor: Constructor