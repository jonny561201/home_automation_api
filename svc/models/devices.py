from dataclasses import dataclass
from typing import List

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

@dataclass_json
@dataclass
class UserDevice:
    id: int
    name: str
    type: str
    ipAddress: str
    ipPort: int
    registered: bool


@dataclass_json
@dataclass
class UserDevices:
    devices: List[UserDevice]