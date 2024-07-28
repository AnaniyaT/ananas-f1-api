from dataclasses import asdict, dataclass

@dataclass
class BaseModel:
    def toJson(self):
        return asdict(self)