#AFV Servo Connection Map
	
	Right brushless motor:servo 0
	Left brushless motor: servo 1
	Steering Servo: servo 2
	# Servo 3 is empty #
	Turret Base: Servo 4
	Turret Arm: Servo 5
	FLIR Base: Servo 6
	FLIR Body: Servo 7

                N  O  T  E! IMPORTANT
Files such as "servo3.py" (from "Pi" folder) are called via ssh commands from the beelink, which has the FLIR operations and data for heat source detection
*** SEE COMMANDS.OUT FILE TO VIEW HOW TO MOVE MULTIPLE SEVRVOS SIMULTANIOUSLY FROM COMMAND LINE ***
The locaiton of these files is "home/AFV/FLIR" on the on-board Beelink computer.
BUT!! The permissions for these files are located in a conda3 environment on the on-board Beelink computer.

How to access conda3:
  open a terminal on the Beelink
Type: 
  conda env list #this is to see availible conda3 environments
Type: 
  conda activate flir #this activates the flir conda environment with all the installed permissions for the AFV project

*** FOR FLIR IMAGE TO WORK ***
When connected to the static network switch, go to this webaddress on Firefox on on-board Beelink (should be a shortcut)
http://10.42.0.45/login?redirectTo=%2F
(go here to log into FLIR A50, the password and username should autopopulate)

*** RealVNC ***
plug pi, and on-board Beelink to network switch
email: afvokstate@gmail.com
password: bnmBNM12!@

*** Below are the Operational FLIR files and a description of how they work

Servo2Combo.py
#Description: This script combines computer vision and robotics control using OpenCV, ONVIF, Paramiko, 
and numpy libraries to manipulate servos based on the visual data captured from an ONVIF camera. The script performs the following functions:

1. **Configuration and Initialization**: Reads camera and Raspberry Pi credentials from environment variables,
    sets up an ONVIF camera connection, retrieves the camera's media profiles, and initializes a video stream.

2. **Video Processing Loop**:
   - Captures frames from the video stream.
   - Converts frames to grayscale and detects hot pixels to identify relevant features.
   - Uses Principal Component Analysis (PCA) to determine the orientation of detected features and calculates their geometric center.
   - Draws an axis along the principal component and displays the orientation angle on the video feed.

3. **Servo Control**:
   - Converts pixel offsets into servo angle adjustments.
   - Sends commands to Raspberry Pi via SSH to adjust servo angles based on visual data, aiming to align the camera's focus with the detected features.
   - Allows manual servo adjustments through keyboard inputs ('u' to update angles based on current frame, 'z' to reset angles).

4. **Graceful Exit**:
   - Ensures servos are reset to a neutral position and all resources are cleanly released upon exiting, either through a signal interruption or manually by pressing 'q'.

The script is designed to dynamically adjust servo positions in real-time, based on visual cues from the video feed, making it suitable for applications like automated tracking or camera stabilization systems.
#input: None
#example run script: python Servo2Combo.py 





Below are the Developmental FLIR files and a description of how they work

trial.py
#Description: This script utilizes OpenCV and PySpin libraries to process and 
#display real-time video and thermal data from an ONVIF camera and a FLIR thermal 
#camera, respectively. It captures video streams, applies a high-pass filter to
#enhance edges, and simultaneously acquires thermal data from a FLIR camera. 
#The video and thermal outputs are displayed in real-time, with the program allowing
#user termination through a keyboard interrupt. Essential resource cleanup is handled 
#gracefully to ensure system stability.
#input: None
#example run script: python trial.py 

ServoCombo,py
#Description: This script integrates ONVIF protocol and computer vision for real-time camera control
#and image processing. It establishes a connection to an ONVIF camera to fetch and display
#a video stream. Using OpenCV, it processes video frames to detect features and calculate 
#their orientation through Principal Component Analysis (PCA). Based on the detected orientation,
#the script dynamically adjusts the positions of servos connected to the camera system to align 
#with these features. The servo commands are sent over SSH using Paramiko, allowing for remote
#control adjustments. The system is designed to enhance automated visual tracking, making 
#adjustments based on the geometric properties of the visual data captured.
#input: None
#example run script: python ServoCombo.py 

combo.py
This Python script is designed to connect to an ONVIF-compliant camera, retrieve video streams, and perform image processing to detect and analyze features in real-time. 
Key components and operations of the script include:

1. **Camera Connection Setup**: The script initializes an ONVIF camera using specified credentials, obtaining a media service and a video stream URI to access the live feed.

2. **Video Stream Capture**: Utilizes OpenCV to capture video from the provided stream URL, which it tries to open and continuously read frames from.

3. **Image Processing**:
   - Converts video frames to grayscale.
   - Applies a threshold to detect 'hot pixels' which could represent specific features or objects of interest depending on the application.
   - Finds contours from these hot pixels to identify distinct shapes or objects within the video frame.

4. **Feature Analysis**:
   - Employs Principal Component Analysis (PCA) to determine the orientation and position of identified contours, calculating their principal axes and rotational angles.
   - Draws these axes on the video frames and overlays the angle information, enhancing visual understanding of object orientation.

5. **Real-time Display**: The processed video frames are displayed in real-time, allowing users to visually monitor changes and detections.

6. **Control and Exit**: Provides a mechanism to safely exit the video stream processing loop and close all resources by pressing the 'q' key.

This script is ideal for applications needing real-time visual tracking or orientation analysis in video streams, such as in surveillance, quality control, or interactive installations.

#input: None
#example run script: python combo.py 

exittest.py
#Description: This Python script registers a function to be executed upon normal interpreter termination using the `atexit` module. The registered function, named `exit`,
#simply prints the word "Test" when invoked. The script then enters an infinite loop with `while True: pass`,
#which keeps the program running indefinitely without performing any operations. The function `exit` will 
#only be called when the Python interpreter is terminating normally
#(e.g., if the program is interrupted with a signal like SIGINT from pressing CTRL+C).

#input: None
#example run script: python exittest.py


flir_servo.py
#Description: This Python script combines video stream processing from an ONVIF-compliant camera with remote servo control through a Raspberry Pi, executed within a multi-threaded architecture. The main functionalities include:

1. **Camera and Video Stream Setup**: Initializes an ONVIF camera using environment variables for the camera's credentials and retrieves the video stream URL.

2. **SSH Connection Setup**: Establishes an SSH connection to a Raspberry Pi for sending servo control commands.

3. **Threaded Command Execution**: Utilizes a separate thread to asynchronously send command lists to the Raspberry Pi. This thread processes commands queued in `command_list` to adjust servos based on image processing results.

4. **Video Processing Loop**:
   - Captures video frames and converts them to grayscale to facilitate feature detection.
   - Identifies hot pixels and contours, using them to compute the orientation of features in the frame via Principal Component Analysis (PCA).
   - Dynamically adjusts servo positions based on the location of detected features relative to the center of the image, aiming to center the camera on these features.

5. **Servo Control**: Sends commands to adjust servo angles via the SSH connection, where commands are managed and executed by the threaded function to reduce latency and enhance responsiveness.

6. **Graceful Exit Handling**: Implements clean-up procedures on exit, including closing the SSH connection and stopping the video capture, facilitated by signal handling and the `atexit` module.

7. **User Interaction**: Provides real-time visual feedback via an OpenCV window and allows user interaction through keyboard inputs to terminate or adjust processing.

This script is particularly suited for applications such as automated monitoring systems, where camera focus and orientation need to be dynamically adjusted based on the visual analysis of the environment.

#input: None
#example run script: python flir_servo.py




onvif_stream2.py
#Description: This Python script utilizes the `ONVIFCamera` library to connect to and control an ONVIF-compliant camera, fetching and displaying its video stream using
OpenCV for real-time processing and visualization:

1. **Camera Configuration**: The script starts by setting up an ONVIF camera using predefined network credentials (IP, port, username, password).

2. **Device Information Retrieval**: Retrieves and prints the manufacturer and model information of the camera using the device management service of ONVIF.

3. **Media Service Initialization**: Initializes the media service of the ONVIF camera to interact with media profiles and streaming capabilities.

4. **Stream Setup**:
   - Fetches media profiles, selects the first one, and uses its token to request the RTSP streaming URI.
   - Prints the retrieved RTSP stream URI to the console.

5. **Video Stream Capture**:
   - Captures the video stream using OpenCV's `VideoCapture` with the RTSP URL.
   - Processes each frame in real-time:
     - Displays the original video frame.
     - Applies a Gaussian blur to create a high-pass filter effect by subtracting the blurred frame from the original.
     - Converts the original frame to grayscale and applies adaptive thresholding to enhance features, converting these to a thermal-like pseudocolor visualization.
   - Displays the modified frames (thermal and high-pass filter effect) in separate OpenCV windows.

6. **Control and Termination**:
   - Provides a real-time video display until the user presses 'q' to quit.
   - Handles errors such as failure to receive frames properly.

This script is ideal for surveillance, remote monitoring, or any application requiring real-time video processing and feature enhancement using an ONVIF-compatible camera.

#input: None
#example run script: python onvif_stream2.py


pixread.py
#Description: This Python script uses OpenCV and matplotlib to perform image processing and feature analysis on thermal images. It includes functions for loading images, 
detecting hot pixels, applying image preprocessing, and calculating the principal component analysis (PCA) to determine the orientation of detected features.
Here's a summary of its main functionalities:

1. **Load Image**: The script loads an image in grayscale from a specified file path.

2. **Detect Hot Pixels**: Applies a threshold to the grayscale image to identify "hot" pixels that exceed a certain temperature threshold.

3. **Preprocess Image**: Applies dilation followed by erosion to the thresholded image to enhance the visibility and separation of features, making them more distinct for further analysis.

4. **Find Contours**: Extracts contours from the preprocessed image, which represent distinct features or regions in the image.

5. **Calculate Orientation via PCA**:
   - Concatenates all points from detected contours and performs PCA to determine the principal direction or orientation of these points.
   - Calculates the angle of the principal axis in degrees, providing an indication of the orientation of the detected features relative to the image frame.

6. **Draw Principal Axis**: Uses the results from PCA to draw the principal axis on the original image, visually representing the main orientation of the detected features.

7. **Display Image**: Utilizes matplotlib to display the modified image with the principal axis and optionally prints the calculated angle to the console.

8. **Conditional Processing**:
   - Handles cases where no contours are found or where the PCA does not yield a meaningful result by either displaying the original image or indicating that no orientation could be calculated.
   - Provides debug output in the console to indicate the process results and any issues encountered.

This script is particularly useful for analyzing thermal images to locate and quantify heat sources, which can be applicable in fields like surveillance, environmental monitoring, and industrial inspections.

#input: None
#example run script: python pixread.py





