from flask import Flask
from flask_cors import CORS

from svc.routes.account_routes import ACCOUNT_BLUEPRINT
from svc.routes.app_routes import APP_BLUEPRINT
from svc.routes.device_routes import DEVICES_BLUEPRINT
from svc.routes.garage_door_routes import GARAGE_BLUEPRINT
from svc.routes.light_routes import LIGHT_BLUEPRINT
from svc.routes.scene_routes import SCENE_BLUEPRINT
from svc.routes.sump_routes import SUMP_BLUEPRINT
from svc.routes.thermostat_routes import THERMOSTAT_BLUEPRINT

app = Flask(__name__)
CORS(app)
app.register_blueprint(APP_BLUEPRINT)
app.register_blueprint(ACCOUNT_BLUEPRINT)
app.register_blueprint(SUMP_BLUEPRINT)
app.register_blueprint(THERMOSTAT_BLUEPRINT)
app.register_blueprint(GARAGE_BLUEPRINT)
app.register_blueprint(LIGHT_BLUEPRINT)
app.register_blueprint(DEVICES_BLUEPRINT)
app.register_blueprint(SCENE_BLUEPRINT)
