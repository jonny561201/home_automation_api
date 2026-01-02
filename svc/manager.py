from flask import Flask
from flask_cors import CORS

from svc.config.security_headers_middleware import add_security_headers
from svc.config.settings_state import Settings
from svc.endpoints.account_routes import ACCOUNT_BLUEPRINT
from svc.endpoints.app_routes import APP_BLUEPRINT
from svc.endpoints.device_routes import DEVICES_BLUEPRINT
from svc.endpoints.garage_door_routes import GARAGE_BLUEPRINT
from svc.endpoints.light_routes import LIGHT_BLUEPRINT
from svc.endpoints.scene_routes import SCENE_BLUEPRINT
from svc.endpoints.sump_routes import SUMP_BLUEPRINT
from svc.endpoints.thermostat_routes import THERMOSTAT_BLUEPRINT

app = Flask(__name__)

CORS(app, origins=Settings.get_instance().allowed_origins)

app.register_blueprint(APP_BLUEPRINT)
app.register_blueprint(ACCOUNT_BLUEPRINT)
app.register_blueprint(SUMP_BLUEPRINT)
app.register_blueprint(THERMOSTAT_BLUEPRINT)
app.register_blueprint(GARAGE_BLUEPRINT)
app.register_blueprint(LIGHT_BLUEPRINT)
app.register_blueprint(DEVICES_BLUEPRINT)
app.register_blueprint(SCENE_BLUEPRINT)
app.after_request(add_security_headers)

