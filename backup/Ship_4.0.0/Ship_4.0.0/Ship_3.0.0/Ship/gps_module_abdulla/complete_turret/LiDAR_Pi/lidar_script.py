import smbus
import time
import sys

# Constants for LIDAR-Lite
LIDAR_BUS = 1
LIDAR_ADDR = 0x62
DISTANCE_REG = 0x8f

# Initialize the I2C bus
bus = smbus.SMBus(LIDAR_BUS)

def read_distance():
    bus.write_byte_data(LIDAR_ADDR, 0x00, 0x04)
    time.sleep(0.02)
    distance = bus.read_word_data(LIDAR_ADDR, DISTANCE_REG)
    distance = (distance >> 8) | ((distance & 0xFF) << 8)
    return distance

def measure():
    return f"Distance: {read_distance()} cm"

def main(primary_command, secondary_command=None):
    """
    Processes the command for the LIDAR script.

    Args:
        primary_command (str): The primary command to process.
        secondary_command (str, optional): An optional secondary command for additional functionality.

    Returns:
        str: The result of the command execution.
    """
    if primary_command == 'measure':
        # Process the measure command
        return measure()
    # Optionally, handle the secondary_command if needed
    # Example:
    # if secondary_command == 'some_other_functionality':
    #     return some_other_functionality()
    else:
        return "No or incorrect command provided."

if __name__ == "__main__":
    # Expect at least one command argument
    if len(sys.argv) > 1:
        # Handle an optional second argument
        secondary_arg = sys.argv[2] if len(sys.argv) > 2 else None
        print(main(sys.argv[1], secondary_arg))
    else:
        print("Usage: python lidar_script.py [command] [optional secondary command]")
