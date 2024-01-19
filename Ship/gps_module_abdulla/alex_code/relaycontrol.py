import RPi.GPIO as GPIO
import time

# Setup, 21 = light, 20 = siren, 26 = pump
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pins = [20]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# Function to toggle a pin high for a specified duration, then low for another duration
def toggle_pin(pin, high_duration, low_duration):
    GPIO.output(pin, True)
    time.sleep(high_duration)
    GPIO.output(pin, False)
    time.sleep(low_duration)

try:
    # Continuously toggling each pin
    while True:
        for pin in pins:
            toggle_pin(pin, .5, 10)  # High for 5 seconds, low for 30 seconds
except KeyboardInterrupt:
    # Cleanup when the program is stopped
    GPIO.cleanup()
