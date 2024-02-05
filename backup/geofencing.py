import serial
import numpy as np

# Input your geofenced area coordinates here
# Example values are given, replace them with your actual values
x_min = 36.1335996  # Replace with your actual value
x_max = 36.1340121  # Replace with your actual value
y_min = -97.0825693  # Replace with your actual value
y_max = -97.0818179  # Replace with your actual value

def configure_serial_port(port='/dev/ttyACM0', baudrate=9600, timeout=1):
    ser = serial.Serial(port, baudrate, timeout=timeout)
    return ser

def convert_to_decimal_degrees(value, direction):
    dlen = 2 if direction in ['N', 'S'] else 3
    degrees = float(value[:dlen])
    minutes = float(value[dlen:])
    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal_degrees *= -1
    return decimal_degrees

def parse_gps_data(gps_data):
    data = gps_data.split(',')
    if data[0] == '$GPGGA' and len(data) > 6:
        latitude = convert_to_decimal_degrees(data[2], data[3])
        longitude = convert_to_decimal_degrees(data[4], data[5])
        return longitude, latitude
    return None, None

def is_point_inside_geofence(matrix):
    lat, lon = matrix[0, 0], matrix[0, 1]
    return x_min <= lat <= x_max and y_min <= lon <= y_max

def read_gps_data(serial_port):
    try:
        gps_matrix = np.zeros((1, 2))  # Matrix to store latitude and longitude
        while True:
            line = serial_port.readline().decode('utf-8').strip()
            if line:
                longitude, latitude = parse_gps_data(line)
                if longitude is not None and latitude is not None:
                    gps_matrix[0, 0], gps_matrix[0, 1] = latitude, longitude
                    if is_point_inside_geofence(gps_matrix):
                        print("Inside of Geofenced Area")
                    else:
                        print("Outside of Geofenced Area")
            else:
                print("No data received or unable to parse GPS data.")
    except KeyboardInterrupt:
        print("Exiting program.")
    except serial.SerialException as e:
        print("Serial error:", e)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    try:
        serial_port = configure_serial_port(port='/dev/ttyACM0', baudrate=9600)
        read_gps_data(serial_port)
    except Exception as e:
        print("Failed to open serial port:", e)
    finally:
        if 'serial_port' in locals() and serial_port.is_open:
            serial_port.close()
