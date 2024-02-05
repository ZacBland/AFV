from adafruit_motorkit import MotorKit
import keyboard
import time

kit = MotorKit()
delay = 0.02
# Initialize the two stepper motors
stepper1 = kit.stepper1  # This was originally stepper2; you can decide which stepper to assign here.
stepper2 = kit.stepper2

print("Press 'q' to quit.")

while True:
    # Check for up arrow key
    if keyboard.is_pressed('up'):
        stepper1.onestep(direction=1)  # Adjust direction if necessary
        time.sleep(delay)  # Introduce a delay to prevent overloading the loop with repeated key detection

    # Check for down arrow key
    elif keyboard.is_pressed('down'):
        stepper1.onestep(direction=0)  # Adjust direction if necessary
        time.sleep(delay)  # Introduce a delay

    # Check for right arrow key
    elif keyboard.is_pressed('right'):
        stepper2.onestep(direction=1)  # Adjust direction if necessary
        time.sleep(delay)  # Introduce a delay

    # Check for left arrow key
    elif keyboard.is_pressed('left'):
        stepper2.onestep(direction=0)  # Adjust direction if necessary
        time.sleep(delay)  # Introduce a delay

    # Check for 'q' key to quit
    elif keyboard.is_pressed('q'):
        stepper1.release()  # Release the first stepper motor
        stepper2.release()  # Release the second stepper motor
        print("Exiting...")
        break

    time.sleep(delay - 0.01)  # Minimal delay to prevent CPU overload

