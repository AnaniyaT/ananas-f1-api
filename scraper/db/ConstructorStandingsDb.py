from sqlite3 import Cursor
from .genericDb.ForeignKey import FK, FKActions
from .genericDb.PrimaryKey import PK
from .genericDb import GenericDatabase, Index
from models import Constructor, ConstructorStandings

class ConstructorStandingsDatabase(GenericDatabase[ConstructorStandings]):
    def __init__(self, cursor: Cursor) -> None:
        super().__init__(
            cursor,
            ConstructorStandings,
            PK(ConstructorStandings, ["year", "position"]),
            "constructorStandings",
            [FK(ConstructorStandings, "constructorId", Constructor, "constructors", "id_", onDelete=FKActions.CASCADE)]
        )
