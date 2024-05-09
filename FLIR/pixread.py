import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(path):
    # Load an image in grayscale
    return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

def find_hot_pixels(image, threshold):
    # Identify hot pixels using thresholding
    _, thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    return thresh

def calculate_angle(eigenvector):
    # Calculate angle in radians and then convert to degrees
    angle_rad = np.arctan2(eigenvector[1], eigenvector[0])
    angle_deg = np.degrees(angle_rad)
    # Normalize the angle to be between 0 and 180 degrees
    angle_deg = angle_deg % 180
    return angle_deg

def calculate_orientation_PCA(contours):
    # Concatenate all contour points into a list before stacking
    all_points = np.vstack([contour.squeeze() for contour in contours])

    # Check if all_points is not empty and has more than one point
    if all_points.shape[0] > 1:
        # Convert all_points to float32 required by cv2.PCACompute
        all_points = np.array(all_points, dtype=np.float32)

        # Compute PCA on the points
        mean, eigenvectors = cv2.PCACompute(all_points, mean=None)

        # Use the first eigenvector as the direction
        axis = eigenvectors[0] * 100  # Scale the axis for visibility

        # Calculate the ends of the principal axis
        p1 = tuple(mean[0] + axis)
        p2 = tuple(mean[0] - axis)

        # Calculate the angle
        angle_deg = calculate_angle(eigenvectors[0])

        return p1, p2, angle_deg
    
    return None, None, None

def draw_axis(image, p1, p2, color=(0, 255, 0)):
    if p1 is not None and p2 is not None:
        cv2.line(image, tuple(map(int, p1)), tuple(map(int, p2)), color, 2)
    return image

def preprocess_image(image, kernel_size=3, iterations=1):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    dilated = cv2.dilate(image, kernel, iterations=iterations)
    processed_image = cv2.erode(dilated, kernel, iterations=iterations)
    return processed_image

def show_image_with_plt(image, title='Image with Principal Axis'):
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()

# Usage
image_path = 'FLIR0041.jpg'  # Update with your path if needed
threshold_value = 250 # Adjust based on your specific temperature threshold

image = load_image(image_path)
assert image is not None, "Image not loaded, check the file path."
hot_pixels = find_hot_pixels(image, threshold_value)
processed_image = preprocess_image(hot_pixels, kernel_size=5, iterations=2)
contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Initialize angle_deg to None
angle_deg = None

# Ensure that calculate_orientation_PCA does not return None before attempting to draw text
result = calculate_orientation_PCA(contours)
if result is not None:
    p1, p2, angle_deg = result
    image_with_line = draw_axis(image.copy(), p1, p2)
else:
    image_with_line = image.copy()
    print("No contours found to calculate orientation.")

# Only draw text if angle_deg is defined
if angle_deg is not None:
    # Draw the angle on the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Angle: {:.2f} degrees".format(angle_deg)
    cv2.putText(image_with_line, text, (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
    print(text)
else:
    print("Angle not calculated.")

show_image_with_plt(image_with_line, 'Principal Axis of Heat Source')

