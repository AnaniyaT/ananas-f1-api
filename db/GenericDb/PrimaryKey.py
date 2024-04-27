import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

from models import BaseModel
from typing import List


class PK:
    """Primary key constraint for a table"""
    def __init__(self, tableClass: BaseModel, columns: List[str]):
        attrs = set(tableClass.__dataclass_fields__.keys())
        for column in columns:
            if column not in attrs:
                message = f"Column {column} not found in {tableClass.__name__}"
                raise ValueError(message)
            
        self.columns = columns
        
    def __str__(self):
        return f"PRIMARY KEY ({', '.join(self.columns)})"