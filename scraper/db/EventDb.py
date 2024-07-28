import sqlite3
from models import Race, RaceEvent
from .genericDb import GenericDatabase, PK, FK, Index, FKActions

class EventDatabase(GenericDatabase[RaceEvent]):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        super().__init__(
            cursor,
            RaceEvent,
            PK(RaceEvent, ["id_"]),
            "events",
            [FK(RaceEvent, "raceId", Race, "races", "id_", onDelete=FKActions.CASCADE)],
            [Index(RaceEvent, "raceIndex", "events", ["raceId"])]
        )