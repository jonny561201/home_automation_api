import RPi.GPIO as GPIO
from svc.manager import create_app


THERMO_PIN = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(THERMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

app = create_app()

if __name__ == '__main__':
    app.run()
