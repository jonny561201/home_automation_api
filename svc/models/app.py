from dataclasses import dataclass
from datetime import date
from typing import Optional

from dataclasses_json import dataclass_json, cfg


cfg.global_config.encoders[date] = date.isoformat
cfg.global_config.decoders[date] = date.fromisoformat


@dataclass_json
@dataclass
class Preference:
    city: str
    tempUnit: str
    measureUnit: str
    garageAlertTime: int = 0
    state: Optional[str] = None
    garageNodeId: Optional[str] = None


@dataclass_json
@dataclass
class Task:
    alarmDays: str
    alarmGroupName: str
    alarmLightGroup: str
    enabled: bool
    hvacMode: str
    hvacStartTemp: int
    hvacStopTemp: int
    taskId: str #GUID
    taskType: str
    alarmTime: Optional[date] = None
    hvacStart: Optional[date] = None
    hvacStop: Optional[date] = None


@dataclass_json
@dataclass
class Tasks:
    tasks: list[Task]
