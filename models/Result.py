from dataclasses import dataclass
from .BaseModel import BaseModel
from .EventType import EventType
from .Constructor import Constructor

@dataclass
class Result(BaseModel):
    eventId: str
    type_: EventType
    position: int
    driverId: str
    driverName: str
    constructorName: str
    laps: int
    
    def __post_init__(self):
        self.constructorId = Constructor.getConstructorId(self.constructorName)

    @staticmethod
    def fromDict(**kwargs):
        type_ = kwargs["type_"]
        if type_ == EventType.RACE or type_ == EventType.SPRINT_RACE:
            return RaceResult(**kwargs)
        elif type_ == EventType.PRACTICE:
            return PracticeResult(**kwargs)
        elif type_ == EventType.QUALIFYING or type_ == EventType.SPRINT_QUALIFYING:
            return QualifyingResult(**kwargs)
        else:
            raise ValueError("Invalid type")
        
    def __str__(self) -> str:
        return f"{self.position} - {self.driverName} - {self.constructorName} - {self.type_}"
            
@dataclass
class RaceResult(Result):
    points: int
    time: str
    constructorId: str = None

@dataclass
class QualifyingResult(Result):
    q1: str
    q2: str
    q3: str
    constructorId: str = None

@dataclass
class PracticeResult(Result):
    time: str
    gap: str
    constructorId: str = None