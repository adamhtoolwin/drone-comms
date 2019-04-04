import RPi.GPIO as GPIO
import time
import sys
IN1 = 27
IN2 = 22
IN3 = 23
IN4 = 24
ENA = 18
ENB = 12

GPIO.setmode(GPIO.BCM)
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

def reverse(tf):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    time.sleep(tf)
    #GPIO.cleanup()

print("close")
reverse(1.5)
GPIO.cleanup()
