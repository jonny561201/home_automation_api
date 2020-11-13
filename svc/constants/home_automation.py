class Mode:
    BLOWER = 'blower'
    COOLING = 'cooling'
    HEATING = 'heating'
    TURN_OFF = 'off'


class Hvac:
    MODE = Mode
    FURNACE = 'furnace'
    AIR_CONDITIONING = 'ac'


class Garage:
    OPEN = True
    CLOSED = False


class Time:
    FIVE_SECONDS = 5
    TEN_SECONDS = 10
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TEN_MINUTE = 600


class Automation:
    APP_NAME = "Soaring Leaf Home Automation"
    HVAC = Hvac
    TIME = Time
    GARAGE = Garage
