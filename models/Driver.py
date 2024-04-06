from dataclasses import dataclass
from .BaseModel import BaseModel
from .Constructor import Constructor

@dataclass
class Driver(BaseModel):
    id: str
    name: str
    shortName: str
    nationality: str
    constructorId: str
    constructor: Constructor