import cv2
import numpy as np
import requests
from time import sleep

# Replace this with the actual URL for fetching the image data from your FLIR A50 camera
IMAGE_API_URL = "rtsp://admin:qzIRge@10.42.0.45/avc/"

# Function to fetch an image from the camera
def fetch_image(url):
    cap = cv2.VideoCapture(url)
    
    ret, frame = cap.read()
    if ret:
        return frame
    else:
        print("Failed to capture frame.")
        return None
    
    cap.release()


# Main loop to display the video stream
try:
    while True:
        frame = fetch_image(IMAGE_API_URL)
        if frame is not None:
            cv2.imshow('FLIR Video Stream', frame)
        else:
            break  # Exit if no frame is returned
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break
finally:
    cv2.destroyAllWindows()