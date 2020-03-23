from svc.manager import create_app

main_app = create_app(__name__)
main_app.run(host='0.0.0.0', port=5000)
