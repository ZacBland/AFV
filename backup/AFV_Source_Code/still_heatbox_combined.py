import cv2
import numpy as np
import os

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

# Usage
rtsp_url = "rtsp://admin:qzIRge@10.42.0.45/avc/"
frame = capture_frame(rtsp_url)

if frame is not None:
    destination_folder = "./flir_images"
    base_filename = "heatmap_boxed"
    save_path = get_next_filename(destination_folder, base_filename)
    apply_heatmap_with_box(frame, save_path)
