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
from utils import Utils

from typing import List, Any, Dict

class Database:
    def __getDatabaseDependencyGraph(self) -> Dict[str, List[str]]:
        dbs = []
        for property_ in dir(self):
            if hasattr(self.__getattribute__(property_), "fks"):
                dbs.append(property_)
        
        dependencyGraph = { db: [] for db in dbs }
        
        for db in dbs:
            for fk in self.__getattribute__(db).fks:
                dependencyGraph[fk.refTableName].append(db)
                
        return dependencyGraph               
    
    
    def __init__(self, path: str = Path(__file__).parent / "db.sqlite3"):
        if not path:
            path = Path(__file__).parent / "db.sqlite3"
        self.__conn = sqlite3.connect(path)
        self.__conn.execute("PRAGMA foreign_keys = 1")
        self.__cursor = self.__conn.cursor()
        
        self.races = RaceDatabase(self.__cursor)
        self.events = EventDatabase(self.__cursor)
        self.circuits = CircuitDatabase(self.__cursor)
        self.constructors = ConstructorDatabase(self.__cursor)
        self.drivers = DriverDatabase(self.__cursor)
        self.results = ResultDatabase(self.__cursor)
        self.driverStandings = DriverStandingsDatabase(self.__cursor)
        self.constructorStandings = ConstructorStandingsDatabase(self.__cursor)

        dependencyGraph = self.__getDatabaseDependencyGraph()
        
        # To get the correct order in which to create the tables
        self.tables = Utils.topologicalSort(dependencyGraph)
    
    
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
        
    def printAttrs(self) -> None:
        for attr in dir(self):
            print(attr)