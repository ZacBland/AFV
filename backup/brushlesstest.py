import RPi.GPIO as GPIO
import keyboard
import time

# Setup
motor_pin = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_pin, GPIO.OUT)
pwm = GPIO.PWM(motor_pin, 50) # 50 Hz (typical for ESCs)
pwm.start(0)

def set_speed(speed):
    pwm.ChangeDutyCycle(speed)

try:
    while True:
        if keyboard.is_pressed('up'):
            print("Moving Forward")
            set_speed(7.5) # Adjust the speed as per your ESC's specifications
        elif keyboard.is_pressed('down'):
            print("Moving Backward")
            set_speed(5) # Adjust the speed as per your ESC's specifications
        else:
            set_speed(0) # Stop the motor
        time.sleep(0.1) # Adjust this delay for responsiveness

except KeyboardInterrupt:
    print("Program stopped")

finally:
    pwm.stop()
    GPIO.cleanup()
