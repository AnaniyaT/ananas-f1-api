from dataclasses import dataclass
from .BaseModel import BaseModel
import json
from utils import Utils

@dataclass
class Constructor(BaseModel):
    name: str
    id_: str = None
    
    def __post_init__(self):
        self.id_ = Constructor.getConstructorId(self.name)
    
    @staticmethod
    def getConstructorId(name: str) -> str:
        bestDistance = 30
        best = None
        constructors = json.load(open("constants/constructors.json"))
        for constructor in constructors:
            names = constructor["names"]
            for n in names:
                editDistance = Utils.editDistance(name.lower(), n.lower())
                if editDistance < bestDistance:
                    bestDistance = editDistance
                    best = [constructor["id"], constructor["name"]]
                    
        if best is None:
            raise Exception(f"Constructor not found: {name}")
                    
        return best[0]