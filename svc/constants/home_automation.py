class Mode:
    BLOWER = 'blower'
    COOLING = 'cooling'
    HEATING = 'heating'
    TURN_OFF = 'off'


class Hvac:
    FURNACE = 'furnace'
    AIR_CONDITIONING = 'ac'


class Garage:
    OPEN = True
    CLOSED = False


class Time:
    FIVE_SECONDS = 5
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TEN_MINUTE = 600


class Automation:
    APP_NAME = "Soaring Leaf Home Automation"
    MODE = Mode()
    HVAC = Hvac()
    TIME = Time()
    GARAGE = Garage()
