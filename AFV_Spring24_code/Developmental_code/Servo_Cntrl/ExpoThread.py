import time
import sys
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import threading

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
        GPIO.output(20, True)
        time.sleep(1)  # Decreased delay to 2 seconds
        GPIO.output(20, False)  # Stop GPIO 20 before GPIO 21
        time.sleep(1)  # GPIO 21 delay
        GPIO.output(21, False)

def servo_and_relays(servo_index, angle, num_iterations):
    servo_thread = threading.Thread(target=move_servo, args=(servo_index, angle))
    relay_thread = threading.Thread(target=cycle_relays, args=(num_iterations,))
    
    servo_thread.start()
    relay_thread.start()
    
    servo_thread.join()
    relay_thread.join()

if len(sys.argv) != 3:
    print("Usage: python script.py <servo_index> <angle>")
    sys.exit(1)

servo_index = int(sys.argv[1])
angle = int(sys.argv[2])
num_iterations = 1

servo_and_relays(servo_index, angle, num_iterations)
