#import GPIO and time
import RPi.GPIO as GPIO
import time

#set GPIO numbering mode and define output pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

# define the number of iterations
num_iterations = 3

# cycle relays
try:
    for _ in range(num_iterations):
        GPIO.output(21, True)
        time.sleep(1)
        GPIO.output(21, False)
        GPIO.output(20, True)
        time.sleep(1)
        GPIO.output(20, False)
        GPIO.output(26, True)
        time.sleep(1)
        GPIO.output(26, False)

except KeyboardInterrupt:
    print("Keyboard interrupt detected. Cleaning up GPIO.")

finally:
    # clean GPIO before finishing
    GPIO.cleanup()
