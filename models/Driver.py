from dataclasses import dataclass
from .BaseModel import BaseModel
from functools import lru_cache
import json

@dataclass
class Driver(BaseModel):
    name: str
    shortName: str
    nationality: str
    constructorId: str
    id_: str = None
    
    def __post_init__(self):
        self.id_ = self.id_ if self.id_ else self.getDriverId(self.name)
    

    @staticmethod
    @lru_cache
    def getDriverId(name: str) -> str:
        with open("constants/drivers.json", "r") as f:
            drivers = json.load(f)
            for driver in drivers:
                if driver["name"] == name:
                    return driver["id"]