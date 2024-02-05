import RPi.GPIO as GPIO
import keyboard
import time

# Pin Definitions
pwm_pin = 12  # GPIO pin 12

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom SOC pin numbers
GPIO.setup(pwm_pin, GPIO.OUT)  # Set the pin to output mode

# Initialize PWM
pwm = GPIO.PWM(pwm_pin, 50)  # Initialize PWM on pwmPin 100Hz frequency

# Start PWM
pwm.start(0)  # Start PWM with 0% duty cycle

def control_motor():
    if keyboard.is_pressed('up'):  # If up arrow key is pressed
        pwm.ChangeDutyCycle(70)  # Adjust this value for forward speed
    elif keyboard.is_pressed('down'):  # If down arrow key is pressed
        pwm.ChangeDutyCycle(30)  # Adjust this value for backward speed
    else:
        pwm.ChangeDutyCycle(0)  # Stop the motor

try:
    while True:
        control_motor()
        time.sleep(0.1)  # Adjust for responsiveness

except KeyboardInterrupt:
    pass

pwm.stop()  # stop PWM
GPIO.cleanup()  # clean up GPIO on CTRL+C exit
