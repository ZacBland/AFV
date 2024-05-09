import sys
import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

kit = ServoKit(channels=8)

def rotate_servos_part1(start_index, end_index, angles):
    for angle in angles:  # List of angles to rotate
        for servo_index in range(start_index, end_index + 1):
            kit.servo[servo_index].angle = angle
            time.sleep(1)

def rotate_servo_4_opposite(angle_6):
    kit.servo[4].angle = 180 - angle_6  # Opposite movement of servo 6

def rotate_servo_5(angle_7):
    kit.servo[5].angle = angle_7  # Same movement as servo 7

def control_relays(num_iterations):
    for _ in range(num_iterations):
        GPIO.output(21, True)
        time.sleep(1)
        GPIO.output(21, False)
        time.sleep(1)

def main():
    try:
        while True:  # Loop until space bar is pressed
            num_iterations = 3  # Number of iterations for relay operation

            # Get angles for servo 6 and 7 from command-line arguments
            angles_part1 = [int(angle) for angle in input("Enter angles for servo 6 and 7 (comma-separated): ").split(",")]

            # Create threads for controlling relays and rotating servos
            relay_thread = threading.Thread(target=control_relays, args=(num_iterations,))
            servo_thread_part1 = threading.Thread(target=rotate_servos_part1, args=(6, 7, angles_part1))
            servo_thread_4 = threading.Thread(target=rotate_servo_4_opposite, args=(angles_part1[0],))
            servo_thread_5 = threading.Thread(target=rotate_servo_5, args=(angles_part1[1],))

            # Start threads
            relay_thread.start()
            servo_thread_part1.start()

            # Wait for the first part of servo rotation to finish
            servo_thread_part1.join()

            # Start the threads for rotating servos 4 and 5
            servo_thread_4.start()
            servo_thread_5.start()

            # Wait for threads to finish
            relay_thread.join()
            servo_thread_4.join()
            servo_thread_5.join()

            print("Press space bar to run again or Ctrl+C to exit.")
            input("Press Enter to continue...")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
