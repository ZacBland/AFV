from onvif import ONVIFCamera
import cv2
import torch
import numpy as np
from PIL import Image, ImageDraw
import super_gradients
from super_gradients.training import models

# Initialize your model

model = models.get("yolo_nas_s",num_classes=5, checkpoint_path='./ckpt_best.pth')
model.eval()
# Initialize your model



device = torch.device("cpu")
model.to(device)


from torchvision.transforms import functional as F




# Replace these variables with your camera's IP address, port, user, and password
my_cam_ip = "10.42.0.45"
my_cam_port = 80
my_cam_user = "fliruser"
my_cam_password = "3vlig"

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

ret, frame = cap.read()
if ret:
    predictions = model.predict(frame, conf=0.50) # You can play with the `conf` and `iou` parameters
    predictions.show()
else:
    print("Failed to capture frame.")


cap.release()
cv2.destroyAllWindows()