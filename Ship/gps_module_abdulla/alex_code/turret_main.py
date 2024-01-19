import cv2
import numpy as np
import os
import time
import math
import socket 

# Constants
STEPS_PER_ROTATION = 200
LIDAR_OFFSET = 5  # LiDAR is 5 cm to the left of the FLIR camera
PIXEL_TO_CM_CONVERSION = 0.1  # Define this based on your setup
ANGLE_CONVERSION_FACTOR = 0.05  # Define this based on your setup

def capture_frame(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    
    ret, frame = cap.read()
    if ret:
        return frame
    else:
        print("Failed to capture frame.")
        return None
    
    cap.release()

def apply_heatmap_with_box(frame, save_path, threshold_ratio=0.95):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply the heatmap color map
    try:
       heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    except cv2.error as e:
        print(f"Error applying color map: {e}")
        return
    
    # Find the coordinates of the maximum pixel value (brightest/hottest point)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    
    # Threshold the grayscale image to isolate the hottest parts
    _, thresholded = cv2.threshold(gray, maxVal * threshold_ratio, 255, cv2.THRESH_BINARY)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create an initial bounding box based on the location of the maximum pixel value
    initial_bbox = (maxLoc[0]-1, maxLoc[1]-1, 3, 3)
    
    # Find the contour containing the initial bounding box, if it exists
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if (x <= initial_bbox[0] <= x + w and y <= initial_bbox[1] <= y + h):
            cv2.rectangle(heatmap, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Draw the box in green color
            break
    
    # Save the heatmap image with the box
    cv2.imwrite(save_path, heatmap)
    print(f"Heatmap with box saved to {save_path}")

def get_next_filename(directory, base_filename):
    # Get a list of all files in the directory
    files = os.listdir(directory)
    
    # Find the highest numbered file that matches the pattern
    max_index = 0
    for file in files:
        if file.startswith(base_filename) and file.endswith(".jpg"):
            try:
                index = int(file[len(base_filename):-4])
                max_index = max(max_index, index)
            except ValueError:
                continue
    
    # Return the next filename
    return os.path.join(directory, f"{base_filename}{max_index + 1}.jpg")

def triangulate_distance(lidar_distance, x_offset):
    """
    Calculate the actual distance to the object using triangulation.
    lidar_distance: Distance measured by the LiDAR
    x_offset: Horizontal offset of the target from the image center
    """
    # Assuming x_offset is in pixels, convert it to cm (requires calibration)
    x_offset_cm = x_offset * PIXEL_TO_CM_CONVERSION  # Define PIXEL_TO_CM_CONVERSION based on your setup

    # Apply Pythagorean theorem for triangulation
    actual_distance = math.sqrt(lidar_distance**2 + (LIDAR_OFFSET + x_offset_cm)**2)
    return actual_distance

def calculate_motor_steps(angle):
    """
    Calculate the number of steps for the motor to rotate a given angle.
    angle: Rotation angle in degrees
    """
    steps_per_degree = STEPS_PER_ROTATION / 360
    return int(angle * steps_per_degree)

def adjust_turret(x, y, image_width, image_height, lidar_distance):
    """
    Adjust the turret based on the coordinates of the target.
    x, y: Coordinates of the target
    image_width, image_height: Dimensions of the image
    lidar_distance: Distance to the target from LiDAR
    """
    x_offset = x - image_width / 2
    y_offset = y - image_height / 2

    # Calculate actual distance to the target
    actual_distance = triangulate_distance(lidar_distance, x_offset)

    # Placeholder for logic to convert x, y offsets to rotation angles
    rotation_angle_x = x_offset * ANGLE_CONVERSION_FACTOR  # Define this factor based on your setup
    rotation_angle_y = y_offset * ANGLE_CONVERSION_FACTOR  # Define this factor based on your setup

    # Calculate steps for the motor
    steps_x = calculate_motor_steps(rotation_angle_x)
    steps_y = calculate_motor_steps(rotation_angle_y)

    # Control the motors based on calculated steps
    # Example: motor_control_x(steps_x), motor_control_y(steps_y)

def get_lidar_data_from_pi(ip_address, port=12345):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_address, port))
            data = s.recv(1024)
        return data.decode()
    except ConnectionError as e:
        print(f"Error connecting to the LiDAR server: {e}")
        return None
    except socket.timeout as e:
        print(f"Timeout occurred: {e}")
        return None
        
# Setting up argparse for CLI
parser = argparse.ArgumentParser(description="Turret Control System")
subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

# Subparser for the move command
move_parser = subparsers.add_parser('move', help='Move the turret')
move_parser.add_argument('x', type=int, help='Change in X coordinate')
move_parser.add_argument('y', type=int, help='Change in Y coordinate')

# Subparser for the lidar command
lidar_parser = subparsers.add_parser('lidar', help='Trigger LiDAR functionality')

# Subparser for the flir command
flir_parser = subparsers.add_parser('flir', help='Capture FLIR stills')

# Main function to parse arguments and call respective functions
def main():
    args = parser.parse_args()
    if args.command == 'move':
        move_turret(args.x, args.y)
    elif args.command == 'lidar':
        trigger_lidar()
    elif args.command == 'flir':
        capture_flir_stills()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

