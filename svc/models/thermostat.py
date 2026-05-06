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


@dataclass_json
@dataclass
class DailyForecast:
    temp: float
    minTemp: float
    maxTemp: float
    description: str


@dataclass_json
@dataclass
class ForecastDay:
    date: str
    minTemp: float
    maxTemp: float
    description: str


@dataclass_json
@dataclass
class ExtendedForecast:
    forecast: list[ForecastDay]
