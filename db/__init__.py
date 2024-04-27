from pathlib import Path
import sys 
sys.path.append(str(Path(__file__).parent.parent))

import sqlite3
from .RaceDb import RaceDatabase
from .EventDb import EventDatabase
from .CircuitDb import CircuitDatabase
from .ConstructorDb import ConstructorDatabase
from .DriverDb import DriverDatabase
from .ResultDb import ResultDatabase
from .DriverStandingsDb import DriverStandingsDatabase
from .ConstructorStandingsDb import ConstructorStandingsDatabase

from typing import List, Any

class Database:
    # Order matters here, Foreign key constraints should be in mind
    tables = [
        "races", "events", "circuits", "constructors", "drivers",
        "results", "driverStandings", "constructorStandings"
        ]
    
    
    def __init__(self, path: str = Path(__file__).parent / "db.sqlite3"):
        self.__conn = sqlite3.connect(path)
        self.__conn.execute("PRAGMA foreign_keys = 1")
        self.__cursor = self.__conn.cursor()

    
    @property
    def races(self) -> RaceDatabase:
        if not hasattr(self, "__races"):
            self.__races = RaceDatabase(self.__cursor)
        
        return self.__races
    
    
    @property
    def events(self) -> EventDatabase:
        if not hasattr(self, "__events"):
            self.__events = EventDatabase(self.__cursor)
        
        return self.__events
    
    
    @property
    def circuits(self) -> CircuitDatabase:
        if not hasattr(self, "__circuits"):
            self.__circuits = CircuitDatabase(self.__cursor)
        
        return self.__circuits
    
    
    @property
    def constructors(self) -> ConstructorDatabase:
        if not hasattr(self, "__constructors"):
            self.__constructors = ConstructorDatabase(self.__cursor)
            
        return self.__constructors
    
    
    @property
    def drivers(self) -> DriverDatabase:
        if not hasattr(self, "__drivers"):
            self.__drivers = DriverDatabase(self.__cursor)
            
        return self.__drivers
    
    
    @property
    def results(self) -> ResultDatabase:
        if not hasattr(self, "__results"):
            self.__results = ResultDatabase(self.__cursor)
            
        return self.__results
    
    
    @property
    def driverStandings(self) -> DriverStandingsDatabase:
        if not hasattr(self, "__driverStandings"):
            self.__driverStandings = DriverStandingsDatabase(self.__cursor)
            
        return self.__driverStandings
    
    
    @property
    def constructorStandings(self) -> ConstructorStandingsDatabase:
        if not hasattr(self, "__constructorStandings"):
            self.__constructorStandings = ConstructorStandingsDatabase(self.__cursor)
            
        return self.__constructorStandings
    
    
    def rawDogg(self, statement: str) -> List[Any]:
        self.__cursor.execute(statement)
        
        return self.__cursor.fetchall()
    
    
    def createTables(self) -> None:
        for table in self.tables:
            self.__getattribute__(table).createTable()
            
    
    def dropTables(self) -> None:
        for table in reversed(self.tables):
            self.__getattribute__(table).dropTable()
            
    
    def resetTables(self) -> None:
        for table in reversed(self.tables):
            self.__getattribute__(table).reset()
            
    
    def initialize(self) -> None:
        for table in self.tables:
            self.__getattribute__(table).initialize()
            
    
    def commit(self) -> None:
        self.__conn.commit()
        
        
    def close(self) -> None:
        self.__conn.close()