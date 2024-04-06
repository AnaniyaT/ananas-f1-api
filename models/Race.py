from dataclasses import dataclass
from .RaceEvent import RaceEvent
from .Circuit import Circuit
from typing import List
from .BaseModel import BaseModel

@dataclass
class Race(BaseModel):
    year: int
    round_: int
    name: str
    location: str
    trackMap: str
    circuit: Circuit | None = None
    events: List[RaceEvent] = None
    id: str = None
    
    def __post_init__(self):
        self.id = f"{self.year}_{self.round_}"
        if self.events is None:
            self.events = []
        if self.circuit is None:
            self.circuit = {}
            
    def addEvent(self, event: RaceEvent) -> None:
        self.events.append(event)
        
    def addEvents(self, events: List[RaceEvent]) -> None:
        self.events.extend(events)
    
    def setCircuit(self, circuit: Circuit) -> None:
        self.circuit = circuit
        
    def __str__(self):
        return f"{self.name} {self.year}"