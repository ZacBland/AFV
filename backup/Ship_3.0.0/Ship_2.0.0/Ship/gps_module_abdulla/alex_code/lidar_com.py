import socket
import smbus
import time

# Constants for LIDAR-Lite
LIDAR_BUS = 1
LIDAR_ADDR = 0x62
DISTANCE_REG = 0x8f

# Initialize the I2C bus for LIDAR
bus = smbus.SMBus(LIDAR_BUS)

def read_distance():
    # Initiate measurement
    bus.write_byte_data(LIDAR_ADDR, 0x00, 0x04)
    
    # Sleep for a short duration allowing LIDAR to perform measurement
    time.sleep(0.02)
    
    # Read two bytes from the distance register
    distance = bus.read_word_data(LIDAR_ADDR, DISTANCE_REG)
    
    # Convert the byte order
    distance = (distance >> 8) | ((distance & 0xFF) << 8)
    
    return distance

def start_server(host='0.0.0.0', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print("Server started, waiting for connections...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")

            try:
                while True:
                    distance = read_distance()
                    client_socket.sendall(str(distance).encode())
            except Exception as e:
                print(f"Error: {e}")
            finally:
                client_socket.close()
                print("Client disconnected")

if __name__ == "__main__":
    start_server()
