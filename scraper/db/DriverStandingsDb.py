from sqlite3 import Cursor
from .genericDb.ForeignKey import FK, FKActions
from .genericDb.PrimaryKey import PK
from .genericDb import GenericDatabase, Index
from models import DriverStandings, Driver

class DriverStandingsDatabase(GenericDatabase[DriverStandings]):
    def __init__(self, cursor: Cursor) -> None:
        super().__init__(
            cursor,
            DriverStandings,
            PK(DriverStandings, ["year", "position"]),
            "driverStandings",
            [FK(DriverStandings, "driverId", Driver, "drivers", "id_", onDelete=FKActions.CASCADE)],
        )