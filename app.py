from svc.manager import create_app
from svc.services.light_service import create_start_light_alarm

create_start_light_alarm()
main_app = create_app(__name__)
main_app.run(host='0.0.0.0', port=5000)
