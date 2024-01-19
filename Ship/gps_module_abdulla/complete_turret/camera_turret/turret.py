from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import sys
import time

def move_stepper(stepper_motor, steps):
    direction = stepper.FORWARD if steps > 0 else stepper.BACKWARD
    for _ in range(abs(steps)):
        stepper_motor.onestep(direction=direction, style=stepper.SINGLE)
        time.sleep(0.025)
    # Consider removing stepper_motor.release() if you want the motor to hold position
    # stepper_motor.release()

def main():
    kit = MotorKit()
    if len(sys.argv) != 3:
        print("Usage: turret.py X Y")
        sys.exit(1)

    try:
        x_steps = int(sys.argv[1])
        y_steps = int(sys.argv[2])
        print(x_steps,y_steps)
    except ValueError:
        print("Invalid arguments. X and Y steps must be integers.")
        sys.exit(1)

    print(f"Parsed steps - X: {x_steps}, Y: {y_steps}")

    move_stepper(kit.stepper1, x_steps)
    move_stepper(kit.stepper2, y_steps)
    print(f"Moved stepper1 by {x_steps} steps and stepper2 by {y_steps} steps.")

if __name__ == "__main__":
    main()