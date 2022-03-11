'''
Original URL https://github.com/respeaker/mic_hat/blob/master/interfaces/pixels.py
'''

import RPi.GPIO as GPIO
import time

BUTTON = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)

while True:
    state = GPIO.input(BUTTON)
    if state:
        print("off")
    else:
        print("on")
    time.sleep(0.1)
