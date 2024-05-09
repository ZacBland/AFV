from onvif import ONVIFCamera
import cv2
import numpy as np
import paramiko

# Replace these variables with your camera's IP address, port, user, and password
my_cam_ip = "10.42.0.45"
my_cam_port = 80
my_cam_user = "fliruser"
my_cam_password = "3vlig"

# Create an ONVIF camera object and get the media service
my_cam = ONVIFCamera(my_cam_ip, my_cam_port, my_cam_user, my_cam_password)
media_service = my_cam.create_media_service()

# Get profiles and use the first profile to get the stream URI
profiles = media_service.GetProfiles()
token = profiles[0].token
stream_uri = media_service.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'RTSP'}, 'ProfileToken': token})
stream_url = stream_uri.Uri
print(f"RTSP Stream URL: {stream_url}")

# Start capturing the video stream
cap = cv2.VideoCapture(stream_url)

def send_servo_command(servo_number, angle):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.42.0.75', username='pi', password='raspberry')  # Use your actual password
    command = f"python servo3.py {servo_number} {int(angle)}"
    stdin, stdout, stderr = ssh.exec_command(command)
    print(f"Command sent: {command}")
    print(stdout.read().decode())  # Optionally print command output
    ssh.close()

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
    
def offset_to_servo_degrees(offset_x, offset_y, img_width, img_height, scale_factor=0.05):
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

if not cap.isOpened():
    print("Error: Could not open video stream.")
else:
    while True:
        ret, frame = cap.read()
        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hot_pixels = find_hot_pixels(gray_frame, 250)  # Adjust threshold based on your specific temperature sensitivity needs
            contours, _ = cv2.findContours(hot_pixels, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                p1, p2, angle_deg = calculate_orientation_PCA(contours)
                frame_with_line = draw_axis(frame, p1, p2) if p1 and p2 else frame
                if angle_deg:
                    cv2.putText(frame_with_line, f"Angle: {angle_deg:.2f} degrees", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    if p1 and p2:
                     # Calculate adjustments needed
                     offset_x, offset_y = calculate_servo_adjustment(frame, p1, p2)
                     new_servo_x_angle, new_servo_y_angle = offset_to_servo_degrees(offset_x, offset_y, frame.shape[1], frame.shape[0])

                        # Send command to servos via SSH (assuming servo interface is already set up)
                    send_servo_command(6, new_servo_x_angle)  # Servo 6 for x-axis adjustment
                    send_servo_command(7, new_servo_y_angle)  # Servo 7 for y-axis adjustment


            else:
                frame_with_line = frame
                print("No contours found to calculate orientation.")

            cv2.imshow('Thermal Image', frame_with_line)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Frame is not received correctly. Exiting...")
            break

cap.release()
cv2.destroyAllWindows()

