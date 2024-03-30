from dataclasses import dataclass
from models.RaceEvent import RaceEvent
from typing import List
from collections.abc import Mapping

@dataclass
class Race:
    year: int
    round_: int
    name: str
    location: str
    trackMap: str
    circuit: Mapping[str:str] = None
    events: List[RaceEvent] = None
    
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
    
    def setCircuit(self, circuit: Mapping[str:str]) -> None:
        self.circuit = circuit
        
    def __str__(self):
        return f"{self.name} {self.year}"