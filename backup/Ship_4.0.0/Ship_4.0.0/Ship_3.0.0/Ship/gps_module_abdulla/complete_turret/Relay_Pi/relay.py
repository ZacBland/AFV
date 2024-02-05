import RPi.GPIO as GPIO
import time
import sys

# Define GPIO pins for each relay
LIGHT_PIN = 21
SIREN_PIN = 20
PUMP_PIN = 26

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup each pin as an output
GPIO.setup(LIGHT_PIN, GPIO.OUT)
GPIO.setup(SIREN_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)

def activate_pin_for_seconds(pin, duration):
    """
    Activates the specified GPIO pin for the specified duration in seconds.
    """
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python relay.py [light/siren/pump] [duration in seconds (optional)]")
        return

    command = sys.argv[1].lower()
    duration = 5  # Default duration

    if len(sys.argv) == 3:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print("Invalid duration. Please enter a valid number.")
            return

    if command == "light":
        activate_pin_for_seconds(LIGHT_PIN, duration)
    elif command == "siren":
        activate_pin_for_seconds(SIREN_PIN, duration)
    elif command == "pump":
        activate_pin_for_seconds(PUMP_PIN, duration)
    else:
        print("Invalid command.")

    # Clean up GPIO on normal exit
    GPIO.cleanup()

if __name__ == "__main__":
    main()
