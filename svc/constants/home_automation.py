class Mime:
    JSON = 'application/json'
    EVENT_STREAM = 'text/event-stream'

class Mode:
    BLOWER = 'blower'
    COOLING = 'cooling'
    HEATING = 'heating'
    TURN_OFF = 'off'
    AUTO = 'auto'


class Hvac:
    MODE = Mode
    QUEUE = 'home-automation-hvac'


class Garage:
    QUEUE = 'home-automation-garage'
    STREAM_HEARTBEAT_SECONDS = 20
    STREAM_READ_TIMEOUT_SECONDS = 60
    STREAM_RECONNECT_SECONDS = 5


class Time:
    FIVE_SECONDS = 5


class AuthClaims:
    ROLES = 'https://soaringleafsolutions.com/roles'
    USER_ID = 'https://soaringleafsolutions.com/user_id'
    AUTH0_ID = 'sub'


class Automation:
    HVAC = Hvac
    GARAGE = Garage
