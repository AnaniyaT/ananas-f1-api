from dataclasses import dataclass

@dataclass
class Result:
    eventId: str
    type_: str
    position: int
    driverId: str
    driverName: str
    constructorName: str
    laps: int

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