from sqlite3 import Cursor
from .GenericDb.ForeignKey import FK
from .GenericDb.PrimaryKey import PK
from .GenericDb import GenericDatabase, Index
from models import DriverStandings, Driver

class DriverStandingsDatabase(GenericDatabase[DriverStandings]):
    def __init__(self, cursor: Cursor) -> None:
        super().__init__(
            cursor,
            DriverStandings,
            PK(DriverStandings, ["year", "position"]),
            "driverStandings",
            [FK(DriverStandings, "driverId", Driver, "drivers", "id_")],
        )