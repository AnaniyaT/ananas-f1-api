
import sqlite3
from models import Circuit
from .GenericDb import GenericDatabase, PK


class CircuitDatabase(GenericDatabase[Circuit]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            Circuit,
            PK(Circuit, ["id_"]),
            "circuits",
        )