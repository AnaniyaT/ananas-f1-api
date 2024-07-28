from dataclasses import dataclass

from .BaseModel import BaseModel
from .EventType import EventType

@dataclass
class RaceEvent(BaseModel):
    raceId: str
    title: str
    date: str
    type_: EventType
    time: str
    gmtOffset: str
    id_: str = None
    
    def __post_init__(self):
        self.id_ = self.formatEventId(self.raceId, self.title)

    @staticmethod
    def formatEventId(raceId: str, title: str) -> str:
        return f"{raceId}_{title}".replace(" ", "_").upper()
    
    @staticmethod
    def getEventTitle(eventId: str) -> str:
        return " ".join(eventId.split("_")[2:])

    @staticmethod
    def getEventYear(eventId: str) -> int:
        return int(eventId.split("_")[0])
    
    @staticmethod
    def getEventRound(eventId: str) -> int:
        return int(eventId.split("_")[1])