from dataclasses import dataclass
from datetime import date
from typing import Optional

from dataclasses_json import dataclass_json, cfg

cfg.global_config.encoders[date] = date.isoformat
cfg.global_config.decoders[date] = date.fromisoformat


@dataclass_json
@dataclass
class SumpLevel:
    currentDepth: float
    warningLevel: int
    averageDepth: float
    latest_date: Optional[date] = None
    depthUnit: str = 'cm'