from onvif import ONVIFCamera
import cv2
# Replace these variables with your camera's IP address, port, user, and password
my_cam_ip = "10.42.0.45"
my_cam_port = 80
my_cam_user = "fliruser"
my_cam_password = "3vlig"

# Create an ONVIF camera object
my_cam = ONVIFCamera(my_cam_ip, my_cam_port, my_cam_user, my_cam_password)

# Get device information
device_info = my_cam.devicemgmt.GetDeviceInformation()
print(f"Manufacturer: {device_info.Manufacturer}")
print(f"Model: {device_info.Model}")
# Get the media service
media_service = my_cam.create_media_service()

# Get profiles
profiles = media_service.GetProfiles()

# Use the first profile and get the token
token = profiles[0].token

# Get stream URI
stream_uri = media_service.GetStreamUri({'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'RTSP'}, 'ProfileToken': token})

print(f"Stream URI: {stream_uri.Uri}")

# Create an ONVIF camera object
my_cam = ONVIFCamera(my_cam_ip, my_cam_port, my_cam_user, my_cam_password)

# Function to get the media service and RTSP URL
def get_stream_uri():
    # Create media service
    media_service = my_cam.create_media_service()
    
    # Get profiles and use the first profile
    profiles = media_service.GetProfiles()
    media_profile = profiles[0]
    
    # Get stream URI
    request = media_service.create_type('GetStreamUri')
    request.ProfileToken = media_profile.token
    request.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
    stream_uri = media_service.GetStreamUri(request)
    
    return stream_uri.Uri

# Get RTSP stream URL from the ONVIF camera
stream_url = get_stream_uri()
print(f"RTSP Stream URL: {stream_url}")

# Start capturing and displaying the video stream
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Could not open video stream.")
else:
    while True:
        ret, frame = cap.read()
        if ret:
            print(frame.shape)
            cv2.imshow('ONVIF Camera Stream', frame)
            blurred = cv2.GaussianBlur(frame, (21, 21), 0)

            # Subtract the blurred frame from the original frame to get a high-pass filter effect
            high_pass = cv2.subtract(frame, blurred)

            # Display the result
            cv2.imshow('High-Pass Filter Result', high_pass)
    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Frame is not received correctly. Exiting...")
            break

cap.release()
cv2.destroyAllWindows()