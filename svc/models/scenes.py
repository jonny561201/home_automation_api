from dataclasses import dataclass

from dataclasses_json import dataclass_json

test = [{
    'name': '',
    'lights': [
        {'group_name': '',
         'group_id': 1,
         'brightness': 255
         }
    ]
}]

@dataclass_json
@dataclass
class LightDetail:
    group_name: str
    group_id: int
    brightness: int


@dataclass_json
@dataclass
class LightScene:
    name: str
    lights: list[LightDetail]