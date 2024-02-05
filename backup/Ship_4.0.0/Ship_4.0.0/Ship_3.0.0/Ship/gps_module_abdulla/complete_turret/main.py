import subprocess
import cv2
import os
import numpy as np


RPI_PASS = 'raspberry'
def generate_rtsp_url(ip_address):
    return f"rtsp://admin:qzIRge@{ip_address}/avc/"

def capture_frame(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    
    ret, frame = cap.read()
    cap.release()  # Release the VideoCapture object

    if ret:
        return frame
    else:
        print("Failed to capture frame.")
        return None
    
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
    
    box_center = None

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if (x <= initial_bbox[0] <= x + w and y <= initial_bbox[1] <= y + h):
            cv2.rectangle(heatmap, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Draw the box
            box_center = (x + w//2, y + h//2)  # Calculate the center of the box
            break

    cv2.imwrite(save_path, heatmap)
    print(f"Heatmap with box saved to {save_path}")

    return box_center
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
def flir_camera_menu():
    # Preset RTSP URL
    ip = input("Enter the IP address: ")
    rtsp_url = generate_rtsp_url(ip)
    frame = capture_frame(rtsp_url)

    if frame is not None:
        destination_folder = "C:/Users/alexa/Desktop/Ship_2.0.0/Ship/gps_module_abdulla/complete_turret/images"
        base_filename = "heatmap_boxed"
        save_path = get_next_filename(destination_folder, base_filename)
        apply_heatmap_with_box(frame, save_path)

def lidar_menu():
    # Assuming send_command_to_pi returns a tuple (output, error)
    result, error = send_command_to_pi("lidar", "measure")

    if error is not None:
        print(f"Error retrieving LiDAR data: {error}")
    else:
        print(f"LiDAR data retrieved: {result}")

def stepper_motors_menu():
    x_amount = int(input("Enter the amount to move the stepper motor in the X direction: "))
    y_amount = int(input("Enter the amount to move the stepper motor in the Y direction: "))

    result, error = send_command_to_pi("turret",x_amount,y_amount)

    if error:
        print(f"Error: {error}")
    else:
        print(f"Stepper motors moved. Result: {result}")

    return result, error

def relay_menu():
    print("\nRelay Control")
    print("1. Pump")
    print("2. Lights")
    print("3. Siren")
    print("4. Return to Main Menu")

    choice = input("Select an option: ")
    command = ""

    if choice == "1":
        command = "pump"
    elif choice == "2":
        command = "light"
    elif choice == "3":
        command = "siren"
    elif choice == "4":
        return None, None
    else:
        print("Invalid choice. Please try again.")
        return None, "Invalid choice"

    result, error = send_command_to_pi("relay", command)

    if error:
        print(f"Error: {error}")
    else:
        print(f"Command '{command}' sent. Result: {result}")

    return result, error
def homing_turret_menu():
    print("Homing Turret...")

    # Capture frame from FLIR camera
    #FLIR IP
    ip = "169.254.213.67"
    rtsp_url = generate_rtsp_url(ip)
    frame = capture_frame(rtsp_url)

    if frame is not None:
        # Process the frame to apply heatmap and find the box
        destination_folder = "Ship/gps_module_abdulla/complete_turret/images"
        base_filename = "heatmap_boxed"
        save_path = get_next_filename(destination_folder, base_filename)
        box_center = apply_heatmap_with_box(frame, save_path)

        if box_center is not None:
            # Assuming frame is a numpy array, get image size
            img_size = frame.shape[1], frame.shape[0]
            
            # Calculate steps for turret based on box center
            x_steps, y_steps = homing_turret(box_center, img_size)
            
            # Send commands to turret to move stepper motors
            result, error = send_command_to_pi("turret", x_steps, y_steps)
            
            if error:
                print(f"Error in moving turret: {error}")
            else:
                print(f"Turret homed. Result: {result}")
        else:
            print("No target identified in the frame.")
    else:
        print("Failed to capture frame from the FLIR camera.")
        
def homing_turret(box_center, img_size, steps_per_rotation=100):
    """
    Move the turret based on the coordinates from the FLIR camera's output.

    Args:
    box_center (tuple): A tuple (x, y) representing the center of the box detected by the FLIR camera.
    img_size (tuple): A tuple (width, height) representing the size of the FLIR camera image in pixels.
    steps_per_rotation (int): The number of steps for a full rotation of the stepper motor.

    Returns:
    tuple: A tuple containing the number of steps for X and Y stepper motors.
    """
    img_center = (img_size[0] // 2, img_size[1] // 2)  # Calculate the center of the image

    # Calculate the difference between the box center and the image center
    delta_x, delta_y = box_center[0] - img_center[0], box_center[1] - img_center[1]

    # Assuming a linear relationship between pixels and steps
    # You may need to adjust this formula based on your actual setup
    steps_x = (delta_x / img_size[0]) * steps_per_rotation
    steps_y = (delta_y / img_size[1]) * steps_per_rotation

    return int(steps_x), int(steps_y)

def main_menu():
    while True:
        print("\nMain Menu")
        print("1. Stepper Motors")
        print("2. FLIR Camera")
        print("3. LiDAR")
        print("4. Relay Control")
        print("5. Homing Turret")
        print("6. Exit")

        choice = input("Select an option: ")
        
        if choice == "1":
            stepper_motors_menu()
        elif choice == "2":
            flir_camera_menu()
        elif choice == "3":
            lidar_menu()
        elif choice == "4":
            relay_menu()
        elif choice == "5":
            homing_turret_menu()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def send_command_to_pi(device_type, command1, command2=None):
    """
    Sends a command to a Raspberry Pi device over SSH based on the device type and returns the output.
    For the turret, it supports sending two separate command fields.

    Args:
    device_type (str): The type of the device (lidar, nozzle, relay, motor, turret, etc.).
    command1 (str): The first part of the command to be executed on the Raspberry Pi.
    command2 (str, optional): The second part of the command, if applicable for the device.

    Returns:
    tuple: A tuple containing the output from the command and an error message if any.
    """
    # IP table mapping device types to their respective IP addresses
    ip_table = {
        "lidar": "169.254.47.131",
        "nozzle": "169.254.226.29",
        "relay": "169.254.174.32",
        "motor": "169.254.15.168",
        "turret": "169.254.40.181"
        # ... add other device IPs as needed
    }

    # Script mapping based on device type
    script_paths = {
        "lidar": "lidar_script.py",
        "turret": "turret.py",
        "relay": "relay.py",
        # ... add other scripts as needed
    }

    device_ip = ip_table.get(device_type)
    if device_ip is None:
        return None, "Device type not found"

    script_path = script_paths.get(device_type)
    if script_path is None:
        return None, "Script for device type not found"
    # Constructing the SSH command
    ssh_command = ["sshpass", "-p", RPI_PASS, "ssh", f"pi@{device_ip}", "python3", f"/home/pi/Desktop/{script_path}"]
    if device_type == "turret":
        # For turret, append both commands as separate arguments
        ssh_command.append(str(command1))
        if command2 is not None:
            ssh_command.append(str(command2))
    else:
        # For other devices
        ssh_command.append(str(command1))
        if command2 is not None:
            ssh_command.append(str(command2))

    try:
        # Execute SSH command
        process = subprocess.run(ssh_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if process.stderr:
            return None, f"Error executing SSH command: {process.stderr}"
        return process.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, f"Failed to send command. Error: {e}"

if __name__ == "__main__":
    main_menu()
