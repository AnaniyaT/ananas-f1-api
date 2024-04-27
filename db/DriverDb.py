import sqlite3
from models import Driver, Constructor
from .GenericDb import GenericDatabase, PK, FK

class DriverDatabase(GenericDatabase[Driver]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            Driver,
            PK(Driver, ["id_"]),
            "drivers",
            [FK(Driver, "constructorId", Constructor, "constructors", "id_")],
        )