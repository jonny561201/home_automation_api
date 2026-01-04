from dataclasses import dataclass
from datetime import date

from dataclasses_json import dataclass_json, cfg

cfg.global_config.encoders[date] = date.isoformat
cfg.global_config.decoders[date] = date.fromisoformat


@dataclass_json
@dataclass
class SumpLevel:
    currentDepth: float
    warningLevel: float
    averageDepth: float
    latest_date: date = None
    depthUnit: str = 'cm'