import sqlite3
from models import Race, Circuit
from .GenericDb import GenericDatabase, PK, FK, Index

class RaceDatabase(GenericDatabase[Race]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            Race,
            PK(Race, ["id_"]),
            "races",
            [FK(Race, "circuitId", Circuit, "circuits", "id_")],
            [Index(Race, "circuitIndex", "races", ["circuitId"])]
        )
            
            