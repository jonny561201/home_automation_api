from dataclasses import dataclass, field
from typing import Dict, List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Device:
    deviceId: str  #GUID


@dataclass
class NodeInfo:
    nodeId: str
    name: str


@dataclass
class DeviceInfo:
    id: str
    ip_address: str
    ip_port: int
    api_key: str
    nodes: Dict[str, NodeInfo] = field(default_factory=dict)


@dataclass_json
@dataclass
class DeviceNodeDetail:
    nodeDevice: int
    nodeName: str


@dataclass_json
@dataclass
class UserDevice:
    deviceId: str
    name: str
    type: str
    registered: bool
    maxNodes: int = 1
    nodes: List[DeviceNodeDetail] = field(default_factory=list)


@dataclass_json
@dataclass
class UserDevices:
    devices: List[UserDevice]