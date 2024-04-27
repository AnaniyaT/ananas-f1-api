from dataclasses import dataclass

from .BaseModel import BaseModel
from .EventType import EventType
from .Result import Result
from typing import List

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