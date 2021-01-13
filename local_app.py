from svc.manager import app
from svc.services.light_service import create_start_light_alarm

if __name__ == '__main__':
    create_start_light_alarm()
    app.run(host='0.0.0.0', port=5000)
