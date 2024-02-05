import serial

def configure_serial_port(port='COM5', baudrate=9600, timeout=1):
    ser = serial.Serial(port, baudrate, timeout=timeout)
    return ser

def is_within_box(current_coords, box_coords):
    """
    Check if the current coordinates are within the given box coordinates.
    
    Args:
    current_coords (tuple): A tuple of (latitude, longitude).
    box_coords (tuple): A tuple of two tuples, representing the top-left and bottom-right
                        corners of the box ((lat1, long1), (lat2, long2)).
    
    Returns:
    bool: True if within the box, False otherwise.
    """
    (lat, lon) = current_coords
    ((lat1, lon1), (lat2, lon2)) = box_coords

    return lat1 <= lat <= lat2 and lon1 <= lon <= lon2

def parse_gps_data(gps_data):
    """
    Parse the GPS data to extract latitude and longitude.
    
    This function needs to be customized based on the format of your GPS data.
    
    Args:
    gps_data (str): The raw GPS data string.
    
    Returns:
    tuple: A tuple containing the latitude and longitude.
    """
    # Implement parsing logic here
    # Example: return (latitude, longitude)
    return (0, 0)  # Placeholder for actual GPS data parsing

def read_and_check_gps_data(serial_port, box_coords):
    while True:
        line = serial_port.readline().decode('utf-8').strip()
        print("GPS Data:", line)
        current_coords = parse_gps_data(line)
        if is_within_box(current_coords, box_coords):
            print("True - Within the Box")
        else:
            print("False - Outside the Box")

if __name__ == "__main__":
    # Define the box coordinates (top-left and bottom-right)
    box_coords = ((lat1, lon1), (lat2, lon2))  # Replace with actual coordinates

    # Configure the serial port
    serial_port = configure_serial_port(port='COM5', baudrate=9600)

    try:
        read_and_check_gps_data(serial_port, box_coords)
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        serial_port.close()