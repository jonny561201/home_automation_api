from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json, cfg

cfg.global_config.encoders[datetime] = datetime.isoformat
cfg.global_config.decoders[datetime] = datetime.fromisoformat


@dataclass_json
@dataclass
class Coordinates:
    latitude: float
    longitude: float


@dataclass_json
@dataclass
class GarageStatus:
    isGarageOpen: bool
    statusDuration: datetime
    coordinates: Coordinates


@dataclass_json
@dataclass
class GarageState:
    isGarageOpen: bool
