import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

kit = ServoKit(channels=8)

def rotate_servos_part1(start_index, end_index):
    for angle in [90, 38, 90, 120, 90]:  # List of angles to rotate
        for servo_index in range(start_index, end_index + 1):
            kit.servo[servo_index].angle = angle
            time.sleep(1)

def rotate_servo_4():
    for angle in [90, 25, 90, 165, 90]:  # List of angles to rotate
        kit.servo[4].angle = angle
        time.sleep(1)

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

            # Define the start and end indexes for the servos to rotate
            start_index_part1 = 5
            end_index_part1 = 7

            # Create threads for controlling relays and rotating servos
            relay_thread = threading.Thread(target=control_relays, args=(num_iterations,))
            servo_thread_part1 = threading.Thread(target=rotate_servos_part1, args=(start_index_part1, end_index_part1))
            servo_thread_4 = threading.Thread(target=rotate_servo_4)

            # Start threads
            relay_thread.start()
            servo_thread_part1.start()

            # Wait for the first part of servo rotation to finish
            servo_thread_part1.join()

            # Start the thread for rotating servo 4
            servo_thread_4.start()

            # Wait for threads to finish
            relay_thread.join()
            servo_thread_4.join()

            print("Press space bar to run again or Ctrl+C to exit.")
            input("Press Enter to continue...")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
