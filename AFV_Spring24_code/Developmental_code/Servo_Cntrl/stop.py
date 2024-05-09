import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

# Initialize GPIO and servo kit
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)  # Assuming you have other GPIO pins as well

kit = ServoKit(channels=8)

def home_servos():
    # Set all servos to their default positions
    for servo_index in range(8):
        kit.servo[servo_index].angle = 90

def cleanup_gpio():
    # Clean up GPIO pins
    GPIO.cleanup()

def main():
    try:
        # Home the servos
        home_servos()

        # Do any additional cleanup or tasks here
        
        # Clean up GPIO
        cleanup_gpio()

        print("All devices homed and turned off.")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Make sure GPIO is cleaned up even if an exception occurs
        cleanup_gpio()

if __name__ == "__main__":
    main()
