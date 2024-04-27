from dataclasses import dataclass
from .BaseModel import BaseModel
from .EventType import EventType
from .Constructor import Constructor

@dataclass(kw_only=True)
class Result(BaseModel):
    eventId: str
    position: int
    driverId: str
    driverNumber: int
    laps: int
    constructorId: str = None
    
    def __post_init__(self):
        self.type_ = EventType.getType(self.eventId.split("_")[2])

    @staticmethod
    def fromDict(**kwargs):
        type_ = EventType.getType((kwargs["eventId"].split("_")[2]))
        
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
    

@dataclass
class QualifyingResult(Result):
    q1: str
    q2: str
    q3: str


@dataclass
class PracticeResult(Result):
    time: str
    gap: str