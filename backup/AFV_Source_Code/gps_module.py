import serial
import time
import sys

def parse_gpgga(line):
    parts = line.split(',')
    # Ensure the sentence is well-formed
    if len(parts) != 15 or parts[0] != "$GPGGA":
        return None

    info = {}
    # Check for a valid fix
    fix_status = parts[6]
    if fix_status == '0':
        info["fix"] = "Invalid"
    elif fix_status == '1':
        info["fix"] = "GPS fix"
    elif fix_status == '2':
        info["fix"] = "DGPS fix"
    else:
        info["fix"] = "Unknown"

    # Parse the number of satellites being tracked
    info["tracked_satellites"] = parts[7]

    # Parse the Horizontal Dilution of Precision (HDOP)
    info["hdop"] = parts[8]

    # Parse the altitude above mean sea level
    info["altitude"] = f"{parts[9]} {parts[10]}"  # value and unit

    # Extract latitude and longitude
    lat = float(parts[2])
    if parts[3] == "S":
        lat = -lat
    lon = float(parts[4])
    if parts[5] == "W":
        lon = -lon

    info["latitude"] = lat
    info["longitude"] = lon

    return info

# Specify your port and baud rate here
port = 'COM4'  # Change this to your actual COM port
baud_rate = 9600

try:
    ser = serial.Serial(port, baud_rate, timeout=1)
    time.sleep(1)  # Let the connection stabilize

    print(f"Reading from {port}")

    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()
        if not line:
            continue

        data = parse_gpgga(line)
        if data:
            print(f"Fix status: {data['fix']}")
            if data['fix'] != "Invalid":
                print(f"Latitude: {data['latitude']}, Longitude: {data['longitude']}")
                print(f"Tracked satellites: {data['tracked_satellites']}, HDOP: {data['hdop']}")
                print(f"Altitude: {data['altitude']}")
            print("--------------------")

except serial.SerialException as e:
    print(f"Could not open or lost connection to the port {port}: {str(e)}")
    sys.exit(1)

except KeyboardInterrupt:
    print("\nStopped by user")

finally:
    if 'ser' in locals():
        ser.close()
