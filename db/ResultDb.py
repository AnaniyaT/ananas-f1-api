
import sqlite3
from typing import List
from models import Constructor, RaceEvent, Result, EventType, QualifyingResult, RaceResult, PracticeResult, Driver
from .GenericDb import GenericDatabase, PK, FK, Index

class ResultDatabase():
    def __getIndices(self, tableName: str) -> List[Index]:
        return [
            Index(Result, "eventIndex", tableName, ["eventId"]),
            Index(Result, "driverIndex", tableName, ["driverId"]),
            Index(Result, "constructorIndex", tableName, ["constructorId"])
        ]
        
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        pk = PK(Result, ["eventId", "driverId"])
        self.pk = pk
        
        fks = [
            FK(Result, "eventId", RaceEvent, "events", "id_"),
            FK(Result, "driverId", Driver, "drivers", "id_"),
            FK(Result, "constructorId", Constructor, "constructors", "id_"),
        ]

        
        self.race = GenericDatabase[RaceResult](
            cursor,
            RaceResult,
            pk,
            "raceResults",
            fks,
            self.__getIndices("raceResults")
        )
        
        self.quali = GenericDatabase[QualifyingResult](
            cursor,
            QualifyingResult,
            pk,
            "qualifyingResults",
            fks,
            self.__getIndices("qualifyingResults")
        )
        
        self.practice = GenericDatabase[PracticeResult](
            cursor,
            PracticeResult,
            pk,
            "practiceResults",
            fks,
            self.__getIndices("practiceResults")
        )
        
        
    def createTables(self) -> None:
        self.race.createTable()
        self.quali.createTable()
        self.practice.createTable()
    
    
    def dropTables(self) -> None:
        self.race.dropTable()
        self.quali.dropTable()
        self.practice.dropTable()
        
    
    def createIndexes(self) -> None:
        self.race.createIndexes()
        self.quali.createIndexes()
        self.practice.createIndexes()
        
    
    def initialize(self) -> None:
        self.createTables()
        self.createIndexes()
        
        
    def reset(self) -> None:
        self.dropTables()
        self.initialize()
        
    
    def getAll(self) -> List[Result]:
        return self.race.getAll() + self.quali.getAll() + self.practice.getAll()
    
    
    def getByEventId(self, eventId: str) -> List[Result]:
        eventTitle = eventId.split("_")[2]
        type_ = EventType.getType(eventTitle)
        
        if type_ == EventType.PRACTICE:
            return self.practice.getByKeysMany(eventId=eventId)
        
        elif type_ == EventType.QUALIFYING:
            return self.quali.getByKeysMany(eventId=eventId)
        
        return self.race.getByKeysMany(eventId=eventId)
    
    
    def insert(self, result: Result) -> None:
        if result.type_ == EventType.PRACTICE:
            return self.practice.insert(result)
        
        if result.type_ == EventType.QUALIFYING:
            return self.quali.insert(result)
        
        self.race.insert(result)
    
    
    def insertMany(self, results: List[Result]) -> None:
        races: List[RaceResult] = []
        qualis: List[QualifyingResult] = []
        practices: List[PracticeResult] = []
        
        for result in results:
            if result.type_ == EventType.RACE:
                races.append(result)
            elif result.type_ == EventType.QUALIFYING:
                qualis.append(result)
            else:
                practices.append(result)
        
        self.race.insertMany(races)
        self.quali.insertMany(qualis)
        self.practice.insertMany(practices)
        
    
    def update(self, result: Result) -> None:
        if result.type_ == EventType.PRACTICE:
            return self.practice.update(result)
        
        if result.type_ == EventType.QUALIFYING:
            return self.quali.update(result)
        
        self.race.update(result)
        
        
    def exists(self, **kwargs) -> bool:
        if "eventId" in kwargs:
            eventTitle = kwargs["eventId"].split("_")[2]
            type_ = EventType.getType(eventTitle)
            
            if type_ == EventType.PRACTICE:
                return self.practice.exists(**kwargs)
            if type_ == EventType.QUALIFYING:
                return self.quali.exists(**kwargs)
            
            return self.race.exists(**kwargs)
        
        return (
            self.practice.exists(**kwargs) or
            self.quali.exists(**kwargs) or 
            self.race.exists(**kwargs)
        )
        
    
    def insertOrUpdate(self, result: Result) -> int:
        """
        Inserts and returns 0 if a result with the same primary keys does not exist, 
        otherwise updates and returns 1
        """
        pk = self.pk.columns
        pkValues = tuple(getattr(result, pk) for pk in pk)
        searchKeys = dict(zip(pk, pkValues))
        
        if self.exists(**searchKeys):
            self.update(result)
            return 1
        else:
            self.insert(result)
            return 0
        
    
    def insertOrUpdateMany(self, results: List[Result]) -> None:
        for result in results:
            self.insertOrUpdate(result)