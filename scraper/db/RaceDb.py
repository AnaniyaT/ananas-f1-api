import sqlite3
from models import Race, Circuit
from .genericDb import GenericDatabase, PK, FK, FKActions, Index

class RaceDatabase(GenericDatabase[Race]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            Race,
            PK(Race, ["id_"]),
            "races",
            [FK(Race, "circuitId", Circuit, "circuits", "id_", onDelete=FKActions.SET_NULL)],
            [Index(Race, "circuitIndex", "races", ["circuitId"])]
        )