class Mime:
    JSON = 'application/json'
    HTML = 'text/html'
    TEXT = 'text/plain'
    XML = 'application/xml'
    JPG = 'image/jpeg'
    PNG = 'image/png'

class Mode:
    BLOWER = 'blower'
    COOLING = 'cooling'
    HEATING = 'heating'
    TURN_OFF = 'off'
    AUTO = 'auto'


class Hvac:
    MODE = Mode
    FURNACE = 'furnace'
    AIR_CONDITIONING = 'ac'


class Garage:
    OPEN = True
    CLOSED = False


class Time:
    TWO_SECONDS = 2
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
