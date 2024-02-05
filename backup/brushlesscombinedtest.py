import RPi.GPIO as GPIO
import keyboard
import time

# Setup
left_motor_pin = 18  # Left motor
right_motor_pin = 12  # Right motor

GPIO.setmode(GPIO.BCM)
GPIO.setup(left_motor_pin, GPIO.OUT)
GPIO.setup(right_motor_pin, GPIO.OUT)

left_pwm = GPIO.PWM(left_motor_pin, 50)  # 50 Hz (typical for ESCs)
right_pwm = GPIO.PWM(right_motor_pin, 50)  # 50 Hz (typical for ESCs)

left_pwm.start(0)
right_pwm.start(0)

def set_speed(speed):
    left_pwm.ChangeDutyCycle(speed)
    right_pwm.ChangeDutyCycle(speed)
    
try:
    while True:
        # Set throttle to max if up arrow is pressed
        if keyboard.is_pressed('up'):
            set_speed(10) 
        # Set throttle to min if down arrow is pressed
        elif keyboard.is_pressed('down'):
            set_speed(5)
        # Else, set throttle to neutral
        else:
            set_speed(7.5)
            
        # Kill program
        if keyboard.is_pressed('esc'):
            print("Exiting program:")
            break
        
        # Delay to prevent excess CPU usage
        time.sleep(0.0125)

except Exception as e:
    print(str(e))
    
finally:
    # Cleanup on exit
    left_pwm.stop()
    right_pwm.stop()
    GPIO.cleanup()
