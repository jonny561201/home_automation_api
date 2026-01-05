from dataclasses import dataclass
from datetime import date
from typing import Optional

from dataclasses_json import dataclass_json, cfg


cfg.global_config.encoders[date] = date.isoformat
cfg.global_config.decoders[date] = date.fromisoformat

@dataclass_json
@dataclass
class Preference:
    isFahrenheit: bool
    isImperial: bool
    city: str
    garageId: int
    garageDoor: str
    tempUnit: str
    measureUnit: str


@dataclass_json
@dataclass
class Task:
    alarmDays: str
    alarmGroupName: str
    alarmLightGroup: str
    alarmTime: Optional[date]
    hvacMode: str
    hvacStart: Optional[date]
    hvacStop: Optional[date]
    hvacStartTemp: int
    hvacStopTemp: int
    taskId: str #GUID
    enabled: bool
    taskType: str


@dataclass_json
@dataclass
class Tasks:
    tasks: list[Task]