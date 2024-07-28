import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))
from enum import Enum

from models import BaseModel

class FKActions(Enum):
    '''Enum for the actions that can be taken on a foreign key constraint'''
    NO_ACTION = "NO ACTION"
    RESTRICT = "RESTRICT"
    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    

class FK:
    """Foreign key constraint for a table"""
    def __init__(
        self, 
        tableClass: BaseModel, 
        column: str, 
        refTableClass: BaseModel, 
        refTableName: str, 
        refColumn: str,
        onDelete: FKActions = None,
        onUpdate: FKActions = None
    ) -> None:
        tableAttrs = [attr for attr in tableClass.__dataclass_fields__.keys()]
        refTableAttrs = [attr for attr in refTableClass.__dataclass_fields__.keys()]
        
        if column not in tableAttrs:
            message = f"Column {column} not found in {tableClass.__name__}"
            raise ValueError(message)
        if refColumn not in refTableAttrs:
            message = f"Column {refColumn} not found in {refTableClass.__name__}"
            raise ValueError(message)
        
        self.column = column
        self.refTableName = refTableName
        self.refColumn = refColumn
        self.onDelete = onDelete
        self.onUpdate = onUpdate
        

    def __str__(self) -> str:
        actions = []
        actions.append(f"ON DELETE {self.onDelete.value}" if self.onDelete else "")
        actions.append(f"ON UPDATE {self.onUpdate.value}" if self.onUpdate else "")
        actions = " ".join(actions)
        
        return f"FOREIGN KEY ({self.column}) REFERENCES {self.refTableName}({self.refColumn}) {actions}"
    