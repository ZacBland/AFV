import serial.tools.list_ports

def list_serial_ports():
    # Lists serial port names
    ports = serial.tools.list_ports.comports()

    # If no ports are found, it's a NoneType, so it's better to handle it as an empty iterable
    for port in ports:
        print(f"Device: {port.device}, Name: {port.name}, Description: {port.description}")

if __name__ == "__main__":
    list_serial_ports()
