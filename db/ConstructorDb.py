import sqlite3
from models import Constructor
from .GenericDb import GenericDatabase, PK, FK

class ConstructorDatabase(GenericDatabase[Constructor]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            Constructor,
            PK(Constructor, ["id_"]),
            "constructors",
        )