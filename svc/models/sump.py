from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from dataclasses_json import dataclass_json, cfg

cfg.global_config.encoders[date] = date.isoformat
cfg.global_config.decoders[date] = date.fromisoformat
cfg.global_config.encoders[datetime] = datetime.isoformat
cfg.global_config.decoders[datetime] = datetime.fromisoformat


@dataclass_json
@dataclass
class SumpLevel:
    currentDepth: float
    warningLevel: int
    averageDepth: Optional[float] = None
    latest_date: Optional[date] = None
    depthUnit: str = 'cm'


@dataclass_json
@dataclass
class SumpReading:
    depth: float
    dateTime: datetime


@dataclass_json
@dataclass
class SumpDailyReading:
    depth: float
    date: date


@dataclass_json
@dataclass
class SumpReadings:
    readings: List[SumpReading] = field(default_factory=list)


@dataclass_json
@dataclass
class SumpDailyReadings:
    readings: List[SumpDailyReading] = field(default_factory=list)