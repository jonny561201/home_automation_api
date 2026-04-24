from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class LightDetail:
    groupName: str
    groupId: int
    brightness: int


@dataclass_json
@dataclass
class LightScene:
    id: str
    name: str
    lights: list[LightDetail]


@dataclass_json
@dataclass
class LightScenes:
    scenes: list[LightScene]