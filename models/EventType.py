from enum import Enum

class EventType(Enum):
    RACE = "RACE"
    PRACTICE = "PRACTICE"
    QUALIFYING = "QUALIFYING"
    SPRINT_RACE = "SPRINT_RACE"
    SPRINT_QUALIFYING = "SPRINT_QUALIFYING"
    
    @staticmethod
    def getType(eventTitle: str) -> 'EventType':
        if eventTitle.lower() == "sprint":
            return EventType.SPRINT_RACE
        if "sprint" in eventTitle.lower():
            return EventType.SPRINT_QUALIFYING
        if "practice" in eventTitle.lower():
            return EventType.PRACTICE
        if "qualifying" in eventTitle.lower():
            return EventType.QUALIFYING
        
        return EventType.RACE
    
    def __str__(self):
        return self.value