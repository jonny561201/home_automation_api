from dataclasses import dataclass
from datetime import datetime
from typing import List

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
    duration: datetime
    coordinates: Coordinates
    doorName: str


@dataclass_json
@dataclass
class GarageState:
    isGarageOpen: bool


@dataclass_json
@dataclass
class GarageDoor:
    garageId: str
    isGarageOpen: bool
    duration: datetime
    doorName: str
    nodeId: str


@dataclass_json
@dataclass
class GarageOverview:
    coordinates: Coordinates
    doors: List[GarageDoor]

