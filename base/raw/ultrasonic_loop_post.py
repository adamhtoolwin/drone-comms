import RPi.GPIO as GPIO
import time
import requests

while(true):
    try:
        GPIO.setmode(GPIO.BOARD)

        PIN_TRIGGER = 7
        PIN_ECHO = 37

        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        print ("Waiting for sensor to settle")

        time.sleep(2)

        print ("Calculating distance")

        GPIO.output(PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(PIN_TRIGGER, GPIO.LOW)

        while GPIO.input(PIN_ECHO)==0:
                pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
                pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        print ("Distance:",distance,"cm")

        if distance > 60:
            post_endpoint = "https://teamdronex.com/api/v1/available"

            available_data = {
                "status": True
            }

            available_data_post = requests.post(post_endpoint, data=available_data)

        else:
            available_data = {
                "status": False
            }

            available_data_post = requests.post(post_endpoint, data=available_data)

    finally:
        GPIO.cleanup()