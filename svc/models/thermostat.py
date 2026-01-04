from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class ThermostatState:
    currentTemp: float
    isFahrenheit: bool
    minThermostatTemp: float
    maxThermostatTemp: float
    mode: str
    desiredTemp: float