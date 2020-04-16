from flask import Flask
from flask_cors import CORS

from svc.routes.app_routes import APP_BLUEPRINT
from svc.routes.device_routes import DEVICES_BLUEPRINT
from svc.routes.garage_door_routes import GARAGE_BLUEPRINT
from svc.routes.light_routes import LIGHT_BLUEPRINT
from svc.routes.sump_routes import SUMP_BLUEPRINT
from svc.routes.thermostat_routes import THERMOSTAT_BLUEPRINT


def create_app(app_name):
    if app_name == '__main__':
        app = Flask(app_name)
        CORS(app)
        app.register_blueprint(APP_BLUEPRINT)
        app.register_blueprint(SUMP_BLUEPRINT)
        app.register_blueprint(THERMOSTAT_BLUEPRINT)
        app.register_blueprint(GARAGE_BLUEPRINT)
        app.register_blueprint(LIGHT_BLUEPRINT)
        app.register_blueprint(DEVICES_BLUEPRINT)

        return app
