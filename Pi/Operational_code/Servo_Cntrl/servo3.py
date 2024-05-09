import time
import sys
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

# Define GPIO pin for the relay
RELAY_PIN = 21

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Function to turn on relay pin
def turn_on_relay():
    GPIO.output(RELAY_PIN, GPIO.HIGH)

# Function to turn off relay pin
def turn_off_relay():
    GPIO.output(RELAY_PIN, GPIO.LOW)

# Function to move servo
def move_servo(servo_index, angle):
    kit.servo[servo_index].angle = angle
    time.sleep(1)

# Initialize servo kit
kit = ServoKit(channels=8)

if len(sys.argv) != 3:
    print("Usage: python script.py <servo_index> <angle>")
    sys.exit(1)

# Turn on relay pin 21
turn_on_relay()

try:
    servo_index = int(sys.argv[1])
    angle = int(sys.argv[2])

    move_servo(servo_index, angle)

except KeyboardInterrupt:
    print("\nProgram stopped by the user.")

finally:
    # Turn off relay pin 21
    turn_off_relay()
    # Clean up GPIO settings
    GPIO.cleanup()
