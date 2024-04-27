from typing import List

from models import BaseModel

class Index(object):
    """Database index for a table"""
    def __init__(self, tableClass: BaseModel, name: str, table: str, columns: List[str]):
        fields = set(tableClass.__dataclass_fields__.keys())
        for column in columns:
            if column not in fields:
                message = f"Column {column} not found in {tableClass.__name__}"
                raise ValueError(message)
            
        self.name = name
        self.table = table
        self.columns = columns

    def __str__(self):
        return f"CREATE INDEX IF NOT EXISTS {self.name} ON {self.table} ({', '.join(self.columns)});"
