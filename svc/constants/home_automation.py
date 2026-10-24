class Mime:
    JSON = 'application/json'
    HTML = 'text/html'
    TEXT = 'text/plain'
    XML = 'application/xml'
    JPG = 'image/jpeg'
    PNG = 'image/png'
    EVENT_STREAM = 'text/event-stream'

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
    QUEUE = 'home-automation-hvac'


class Garage:
    OPEN = True
    CLOSED = False
    QUEUE = 'home-automation-garage'
    STREAM_HEARTBEAT_SECONDS = 20
    STREAM_READ_TIMEOUT_SECONDS = 60
    STREAM_RECONNECT_SECONDS = 5


class Time:
    TWO_SECONDS = 2
    FIVE_SECONDS = 5
    TEN_SECONDS = 10
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TEN_MINUTE = 600


class AuthClaims:
    ROLES = 'https://soaringleafsolutions.com/roles'
    USER_ID = 'https://soaringleafsolutions.com/user_id'
    AUTH0_ID = 'sub'


class Automation:
    APP_NAME = "Soaring Leaf Home Automation"
    HVAC = Hvac
    TIME = Time
    GARAGE = Garage
