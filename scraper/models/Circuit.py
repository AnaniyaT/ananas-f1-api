import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dataclasses import dataclass
import json
from .BaseModel import BaseModel
from utils import Utils


@dataclass
class Circuit(BaseModel):
    name: str
    numberOfLaps: int
    length: float
    raceDistance: float
    lapRecord: str
    firstGrandPrix: int
    id_: str = None
    
    def __str__(self):
        return self.name
    
    def __post_init__(self):
        self.id_ = self.getCircuitId(self.name)
    
    @staticmethod
    def fromDict(**kwargs):
        return Circuit(**kwargs)
    
    @staticmethod
    def getCircuitId(name: str):
        with open("constants/circuits.json") as f:
            circuits = json.load(f)
            bestMatch = None
            bestMatchDistance = 20
            
            for circuit in circuits:
                distance = Utils.editDistance(circuit["name"], name)
                if distance < bestMatchDistance:
                    bestMatch = circuit
                    bestMatchDistance = distance
                    
        return bestMatch["id"] if bestMatch else None
            

    