import RPi.GPIO as GPIO
import time
import sys
IN1 = 27
IN2 = 22
IN3 = 23
IN4 = 24
ENA = 18
ENB = 12
try:
      GPIO.setmode(GPIO.BCM)
      PIN_TRIGGER = 4
      PIN_ECHO = 26
      GPIO.setup(PIN_TRIGGER, GPIO.OUT)
      GPIO.setup(PIN_ECHO, GPIO.IN)
      GPIO.output(PIN_TRIGGER, GPIO.LOW)
      GPIO.setup(IN1, GPIO.OUT)
      GPIO.setup(IN2, GPIO.OUT)
      GPIO.setup(IN3, GPIO.OUT)
      GPIO.setup(IN4, GPIO.OUT)
      GPIO.setup(ENA, GPIO.OUT)
      GPIO.setup(ENB, GPIO.OUT)
      p=GPIO.PWM(ENA,3450)
      s=GPIO.PWM(ENB,3450)
      p.start(100)
      s.start(100)
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
          GPIO.output(IN1, GPIO.LOW)
          GPIO.output(IN2, GPIO.HIGH)
          GPIO.output(IN3, GPIO.LOW)
          GPIO.output(IN4, GPIO.HIGH)
          time.sleep(1.5)
      
finally:      
    GPIO.cleanup()
