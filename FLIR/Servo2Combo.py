from onvif import ONVIFCamera
import cv2
import numpy as np
import paramiko
import os
import time
import sys
import signal

# Configuration via environment variables
my_cam_ip = os.getenv('CAM_IP', '10.42.0.45')
my_cam_port = int(os.getenv('CAM_PORT', 80))
my_cam_user = os.getenv('CAM_USER', 'fliruser')
my_cam_password = os.getenv('CAM_PASSWORD', '3vlig')
pi_password = os.getenv('PI_PASSWORD', 'raspberry')

# Setup camera and media service
my_cam = ONVIFCamera(my_cam_ip, my_cam_port, my_cam_user, my_cam_password)
media_service = my_cam.create_media_service()
profiles = media_service.GetProfiles()
stream_uri = media_service.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'RTSP'}, 'ProfileToken': profiles[0].token})
stream_url = stream_uri.Uri
print(f"RTSP Stream URL: {stream_url}")

# Video capture setup
cap = cv2.VideoCapture(stream_url)

# Initialize servo positions
current_servo_x_angle = 90
current_servo_y_angle = 90

def exit_gracefully(signal, frame):
    print("\nExiting gracefully...")
    # Set all servos to 90 degrees
    send_servo_commands(6, 90)
    send_servo_commands(7, 90)
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)

def calculate_servo_adjustment(image, p1, p2):
    # Image center
    img_center_x, img_center_y = image.shape[1] / 2, image.shape[0] / 2

    # Line center
    line_center_x = (p1[0] + p2[0]) / 2
    line_center_y = (p1[1] + p2[1]) / 2

    # Calculate offset
    offset_x = line_center_x - img_center_x
    offset_y = line_center_y - img_center_y

    return offset_x, offset_y
    
def offset_to_servo_degrees(offset_x, offset_y, img_width, img_height, scale_factor=0.17):
    # Convert pixel offset to servo degrees
    # Calculate adjustment as a proportion of the image dimension scaled by a factor
    servo_adjust_x = -offset_x / img_width * scale_factor * 180
    servo_adjust_y = -offset_y / img_height * scale_factor * 180

    # Calculate new servo angles based on the initial position of 90 degrees
    new_servo_x_angle = 90 + servo_adjust_x
    new_servo_y_angle = 90 + servo_adjust_y

    return new_servo_x_angle, new_servo_y_angle

def find_hot_pixels(image, threshold):
    _, thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return thresh

def calculate_orientation_PCA(contours):
    all_points = np.vstack([contour.squeeze() for contour in contours])
    if all_points.shape[0] > 1:
        all_points = np.array(all_points, dtype=np.float32)
        mean, eigenvectors = cv2.PCACompute(all_points, mean=None)
        axis = eigenvectors[0] * 100  # Scale the axis for visibility
        p1 = tuple(mean[0] + axis)
        p2 = tuple(mean[0] - axis)
        angle_deg = np.degrees(np.arctan2(eigenvectors[1][0], eigenvectors[0][0])) % 180
        return p1, p2, angle_deg
    return None, None, None

def draw_axis(image, p1, p2, color=(0, 255, 0)):
    if p1 is not None and p2 is not None:
        cv2.line(image, tuple(map(int, p1)), tuple(map(int, p2)), color, 2)
    return image
    

def send_servo_commands(servo_numbers, angles):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('10.42.0.75', username='pi', password=pi_password)
        commands = [f"python servo3.py {servo_number} {int(angle)}" for servo_number, angle in zip(servo_numbers, angles)]
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            print(f"Command sent: {command}")
            print(stdout.read().decode())
    except Exception as e:
        print(f"Failed to send SSH command: {e}")
    finally:
        ssh.close()
# Image processing and servo adjustment logic
try:
    if not cap.isOpened():
        print("Error: Could not open video stream.")
    else:
        previous_x_angle, previous_y_angle = 90, 90  # Initial angles
        while True:
            ret, frame = cap.read()
            if ret:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hot_pixels = find_hot_pixels(gray_frame, 250)
                contours, _ = cv2.findContours(hot_pixels, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    p1, p2, angle_deg = calculate_orientation_PCA(contours)
                    if p1 and p2:
                        frame_with_line = draw_axis(frame, p1, p2)
                        cv2.putText(frame_with_line, f"Angle: {angle_deg:.2f} degrees", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('u'):  # Press 'u' to update
                            offset_x, offset_y = calculate_servo_adjustment(frame, p1, p2)
                            if current_servo_x_angle == 90 and current_servo_y_angle == 90:
                                # First press of 'u', use initial servo angles (90, 90)
                                new_servo_x_angle, new_servo_y_angle = offset_to_servo_degrees(offset_x, offset_y, frame.shape[1], frame.shape[0])
                            else:
                                # Subsequent presses of 'u', use current servo angles
                                new_servo_x_angle, new_servo_y_angle = offset_to_servo_degrees(offset_x, offset_y, frame.shape[1], frame.shape[0])
                                new_servo_x_angle += current_servo_x_angle - 90
                                new_servo_y_angle += current_servo_y_angle - 90
                            
                            if abs(new_servo_x_angle - current_servo_x_angle) > 1 or abs(new_servo_y_angle - current_servo_y_angle) > 1:
                                
                                opposite_angle_for_servo_4 = 180 - new_servo_x_angle
                                # Sending commands for servo 6 and servo 4 simultaneously with opposite movements
                                send_servo_commands([6, 4], [new_servo_x_angle, opposite_angle_for_servo_4])
                                # Sending commands for servo 7 and servo 5 simultaneously
                                send_servo_commands([7, 5], [new_servo_y_angle, new_servo_y_angle])
                                current_servo_x_angle, current_servo_y_angle = new_servo_x_angle, new_servo_y_angle
                                time.sleep(2) 
                        elif key == ord('q'):
                            break
                        elif key == ord('z'):
                            # Sending commands to set all servo angles to zero
                            send_servo_commands([4, 5, 6, 7], [90, 90, 90, 90])
                    else:
                        frame_with_line = frame
                else:
                    frame_with_line = frame
                    print("No contours found to calculate orientation.")
                cv2.imshow('Thermal Image', frame_with_line)
            else:
                print("Frame is not received correctly. Exiting...")    
            
finally:
    # Set all servos to 90 degrees upon exiting
    exit_gracefully(None, None)

