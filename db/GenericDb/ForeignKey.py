import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from models import BaseModel

class FK:
    """Foreign key constraint for a table"""
    def __init__(self, tableClass: BaseModel, column: str, refTableClass: BaseModel, refTableName: str, refColumn: str):
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
        

    def __str__(self):
        return f"FOREIGN KEY ({self.column}) REFERENCES {self.refTableName}({self.refColumn})"
    