from playwav import play_wav
import RPi.GPIO as GPIO
import time

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)


while True:
    state = GPIO.input(BUTTON)
    if not (state): # button is pressed
        play_wav('../police-siren.wav')
    time.sleep(0.1)