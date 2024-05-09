import time
import sys
from adafruit_servokit import ServoKit
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

kit = ServoKit(channels=8)

def move_servo(servo_index, angle):
    kit.servo[servo_index].angle = angle
    time.sleep(1)

def cycle_relays(num_iterations):
    for _ in range(num_iterations):
        GPIO.output(21, True)
        time.sleep(2)
        GPIO.output(21, False)
        GPIO.output(20, True)
        time.sleep(1)
        GPIO.output(20, False)
        GPIO.output(26, True)
        time.sleep(1)
        GPIO.output(26, False)
        
num_iterations = 2  

cycle_relays(num_iterations)

if len(sys.argv) != 3:
    print("Usage: python script.py <servo_index> <angle>")
    sys.exit(1)

servo_index = int(sys.argv[1])
angle = int(sys.argv[2])
move_servo(servo_index, angle)




