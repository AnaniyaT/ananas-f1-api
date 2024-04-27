from sqlite3 import Cursor
from .GenericDb.ForeignKey import FK
from .GenericDb.PrimaryKey import PK
from .GenericDb import GenericDatabase, Index
from models import Constructor, ConstructorStandings

class ConstructorStandingsDatabase(GenericDatabase[ConstructorStandings]):
    def __init__(self, cursor: Cursor) -> None:
        super().__init__(
            cursor,
            ConstructorStandings,
            PK(ConstructorStandings, ["year", "position"]),
            "constructorStandings",
            [FK(ConstructorStandings, "constructorId", Constructor, "constructors", "id_")]
        )
