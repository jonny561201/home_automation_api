import RPi.GPIO as GPIO
from svc.manager import app

THERMO_PIN = 11


GPIO.setmode(GPIO.BOARD)
GPIO.setup(THERMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == '__main__':
    app.run()
