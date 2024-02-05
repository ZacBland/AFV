import RPi.GPIO as GPIO
import time

# Pin Definitions
pwm_pin = 12 # GPIO pin 12

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom SOC pin numbers
GPIO.setup(pwm_pin, GPIO.OUT)  # Set the pin to output mode

# Initialize PWM
pwm = GPIO.PWM(pwm_pin, 50)  # Initialize PWM on pwmPin 100Hz frequency

# Start PWM
pwm.start(0)  # Start PWM with 0% duty cycle

try:
    while True:
        # Increase duty cycle: 0~100
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)

        # Decrease duty cycle: 100~0
        for dc in range(100, -1, -5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)

except KeyboardInterrupt:
    pass

pwm.stop()  # stop PWM
GPIO.cleanup()  # clean up GPIO on CTRL+C exit
