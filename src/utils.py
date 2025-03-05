import json
from dataclasses import asdict, dataclass


@dataclass
class BaseDataclassConverter:
    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(asdict(self))
