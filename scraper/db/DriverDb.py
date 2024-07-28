import sqlite3
from models import Driver, Constructor
from .genericDb import GenericDatabase, PK, FK, FKActions

class DriverDatabase(GenericDatabase[Driver]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            Driver,
            PK(Driver, ["id_"]),
            "drivers",
            [FK(Driver, "constructorId", Constructor, "constructors", "id_", onDelete=FKActions.SET_NULL)],
        )