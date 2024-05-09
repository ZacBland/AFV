from onvif import ONVIFCamera
import cv2
import numpy as np
import paramiko
import os
import time
import sys
import signal
import atexit
import threading

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
stream_uri = media_service.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'UDP'}, 'ProfileToken': profiles[0].token})
stream_url = stream_uri.Uri
print(f"RTSP Stream URL: {stream_url}")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.42.0.75', username='pi', password=pi_password)

global command_list
command_list = []
    
def execute_thread(name):
    while thread_running:
        while command_list:
            if not thread_running:
                break
            command = command_list.pop()
            stdin, stdout, stderr = ssh.exec_command(command)
            if not thread_running:
                break

# Video capture setup
cap = cv2.VideoCapture(stream_url)
global frame
frame = None
thread = None
global thread_running
thread_running = True
execute = threading.Thread(target=execute_thread, args=(1,))
execute.start()
print("started thread")

# Initialize servo positions
current_servo_x_angle = 90
current_servo_y_angle = 90

def exit_gracefully(signal=None, frame=None):
    print("\nExiting gracefully...")
    # Set all servos to 90 degrees
    #send_servo_commands(6, 90)
    #send_servo_commands(7, 90)
    cv2.destroyAllWindows()
    print("released capture")
    ssh.close()
    execute.join()
    print("released thread")
    sys.exit(0)

signal.signal(signal.SIGINT, exit_gracefully)
atexit.register(exit_gracefully)

def find_hot_pixels(image, threshold):
    _, thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return thresh

def calculate_orientation_PCA(contours):
    try:
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
    except Exception as e:
        print(e)

def draw_axis(image, p1, p2, color=(0, 255, 0)):
    if p1 is not None and p2 is not None:
        cv2.line(image, tuple(map(int, p1)), tuple(map(int, p2)), color, 2)
    return image

def send_servo_commands(servo_numbers, angles):
    commands = [f"./servo {servo_number} {int(angle)}" for servo_number, angle in zip(servo_numbers, angles)]
    
    for command in commands:
        command_list.append(command)
        #stdin, stdout, stderr = ssh.exec_command(command)
        #print(f"Command sent: {command}")

# Image processing and servo adjustment logic

#print(execute.__getattribute__("command_list"))

current_servo_x_angle = 90
current_servo_y_angle = 90
send_servo_commands([6], [current_servo_x_angle])
send_servo_commands([7], [current_servo_y_angle])

try:
    if not cap.isOpened():
        print("Error: Could not open video stream.")
    else:
        send_time = time.time()
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
                        #cv2.putText(frame_with_line, f"Angle: {angle_deg:.2f} degrees", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        
                        key = cv2.waitKey(1) & 0xFF
                        if time.time() - send_time > 0.08:
                            
                            send_time = time.time()
                            #print("Update")
                            
                            img_center_x, img_center_y = frame.shape[1] / 2, frame.shape[0] / 2

                            # Line center
                            line_center_x = (p1[0] + p2[0]) / 2
                            line_center_y = (p1[1] + p2[1]) / 2

                            error = 150

                            if line_center_x - img_center_x < -error:
                                current_servo_x_angle += 1
                            elif line_center_x - img_center_x > error:
                                current_servo_x_angle -= 1
                            send_servo_commands([6], [current_servo_x_angle])

                            if line_center_y - img_center_y > error:
                                current_servo_y_angle -= 1
                            elif line_center_y - img_center_y < -error:
                                current_servo_y_angle += 1
                            send_servo_commands([7], [current_servo_y_angle])

                            
                                
                        if key == ord('q'):
                            break
                        elif key == ord('z'):
                            # Sending commands to set all servo angles to zero
                            send_servo_commands([6, 7], [90, 90])
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
    thread_running = False
    exit_gracefully(None, None)

