import sys
from pathlib import Path

from models import BaseModel
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Generic, TypeVar, List, Tuple
from .ForeignKey import FK, FKActions
from .PrimaryKey import PK
from .Index import Index
import sqlite3


T = TypeVar("T")

class GenericDatabase(Generic[T]):
    def __init__(
        self, 
        cursor: sqlite3.Cursor, 
        type_: BaseModel, 
        primaryKey: PK, 
        tableName: str = None, 
        foreignKeys: List[FK] = [],
        indexes: List[Index] = []
    ) -> None:
        
        self.type = type_
        self.__cursor = cursor
        
        # table info
        self.tableName = tableName if tableName else type_.__name__
        self.pk = primaryKey
        self.fks = foreignKeys
        self.indexes = indexes
        
        # statements 
        self.createTableStatement = self.getCreateTableStatement(
            type_, primaryKey, foreignKeys
        )
        self.dropTableStatement = f"DROP TABLE IF EXISTS {self.tableName}"
        self.selectAllStatement = f"SELECT * FROM {self.tableName}"
        
        
    def __getFields(self) -> List[str]:
        return [field for field in self.type.__dataclass_fields__.keys()]
        
        
    def getCreateTableStatement(
        self, 
        type_: BaseModel, 
        primaryKey: PK,
        foreignKeys: List[FK]
    ) -> str:
        
        typeMap = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL"
        }
        
        fragments = [
            f"{attribute.name} {typeMap.get(attribute.type, 'TEXT')}"
            for attribute in type_.__dataclass_fields__.values()
        ]
        
        fragments.append(str(primaryKey))
        fragments.extend(str(fk) for fk in foreignKeys)
        
        statement = f"CREATE TABLE IF NOT EXISTS {self.tableName} ({', '.join(fragments)})"
        
        return statement
    
    
    def createTable(self) -> None:
        self.__cursor.execute(self.createTableStatement)
        
    
    def dropTable(self) -> None:
        self.__cursor.execute(self.dropTableStatement)
        
    
    def createIndexes(self) -> None:
        for index in self.indexes:
            self.__cursor.execute(str(index))
            
            
    def initialize(self) -> None:
        self.createTable()
        self.createIndexes()
        
            
    def reset(self) -> None:
        self.dropTable()
        self.initialize()
    
    
    def insertStatement(self, fields: List[str]) -> str:
        formattedFields = ", ".join(fields)
        formattedValues = ", ".join("?" for _ in fields)
        
        return f"INSERT INTO {self.tableName} ({formattedFields}) VALUES ({formattedValues})"
    
    
    def getByKeysStatement(self, **kwargs) -> str:
        formattedKeys = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        
        return f"SELECT * FROM {self.tableName} WHERE {formattedKeys}"
        
    
    def insert(self, instance: T) -> None:
        fields = self.__getFields()
        values = tuple(getattr(instance, field) for field in fields)
        
        self.__cursor.execute(self.insertStatement(fields), values)
        
    
    def getAll(self) -> List[T]:
        self.__cursor.execute(self.selectAllStatement)
        
        instances = [
            self.type(
                **dict(zip(self.__getFields(), row))
            )
            
            for row in self.__cursor.fetchall()
        ]
        
        return instances
    
    
    def getByKeys(self, **kwargs) -> T:
        self.__cursor.execute(self.getByKeysStatement(**kwargs), tuple(kwargs.values()))
        
        row = self.__cursor.fetchone()
        
        return self.type(
            **dict(zip(self.__getFields(), row))
        )
        
        
    def getByKeysMany(self, **kwargs) -> List[T]:
        self.__cursor.execute(self.getByKeysStatement(**kwargs), tuple(kwargs.values()))
        
        instances = [
            self.type(
                **dict(zip(self.__getFields(), row))
            )
            
            for row in self.__cursor.fetchall()
        ]
        
        return instances
        
    
    def insertMany(self, instances: List[T]) -> None:
        fields = self.__getFields()
        values = [tuple(getattr(instance, field) for field in fields) for instance in instances]
        
        self.__cursor.executemany(self.insertStatement(fields), values)
    
    
    def update(self, instance: T) -> None:
        fields = self.__getFields()
        values = tuple(getattr(instance, field) for field in fields)
        pk = self.pk.columns
        pkValues = tuple(getattr(instance, pk) for pk in pk)
        searchKeys = dict(zip(pk, pkValues))
        
        formattedKeys = " AND ".join(f"{key} = ?" for key in searchKeys.keys())
        
        self.__cursor.execute(
            f"UPDATE {self.tableName} SET {', '.join(f'{field} = ?' for field in fields)} WHERE {formattedKeys}",
            values + tuple(searchKeys.values())
        )
        
        
    def delete(self, **kwargs) -> None:
        formattedKeys = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        
        self.__cursor.execute(
            f"DELETE FROM {self.tableName} WHERE {formattedKeys}", tuple(kwargs.values())
        )
        
    
    def exists(self, **kwargs) -> bool:
        formattedKeys = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        
        self.__cursor.execute(
            f"SELECT COUNT(*) FROM {self.tableName} WHERE {formattedKeys}", tuple(kwargs.values())
        )
        
        return self.__cursor.fetchone()[0] > 0
    
    
    def insertOrUpdate(self, instance: T) -> int:
        """
        Inserts and returns 0 if an instance with the same primary keys does not exist, 
        otherwise updates and returns 1
        """
        pk = self.pk.columns
        pkValues = tuple(getattr(instance, pk) for pk in pk)
        searchKeys = dict(zip(pk, pkValues))
        
        if self.exists(**searchKeys):
            self.update(instance)
            return 1
        else:
            self.insert(instance)
            return 0
        
    
    def insertOrUpdateMany(self, instances: List[T]) -> None:
        for instance in instances:
            self.insertOrUpdate(instance)
            
            