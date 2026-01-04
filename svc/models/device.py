from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Device:
    deviceId: str  #GUID


@dataclass_json
@dataclass
class DoorDeviceDetails:
    doorId: int
    doorName: str


@dataclass_json
@dataclass
class DeviceNode:
    availableNodes: int
    device: DoorDeviceDetails