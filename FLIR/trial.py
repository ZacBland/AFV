import cv2
import PySpin  # Import the PySpin library

def acquire_thermal_data(camera):
    # Set acquisition mode to continuous
    camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

    # Start acquisition
    camera.BeginAcquisition()

    # Capture a thermal image
    image_result = camera.GetNextImage()
    thermal_data = image_result.GetThermalData()

    # Release image
    image_result.Release()

    return thermal_data

def main():
    cap = cv2.VideoCapture('your_video_stream_url_here')

    # Initialize the FLIR camera
    system = PySpin.System.GetInstance()  # Initialize the system
    cam_list = system.GetCameras()  # Get connected cameras

    if cam_list.GetSize() == 0:
        print("No FLIR cameras found. Exiting...")
        return

    flir_camera = cam_list.GetByIndex(0)  # Get the first camera
    flir_camera.Init()  # Initialize the camera

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                print(frame.shape)
                cv2.imshow('ONVIF Camera Stream', frame)
                blurred = cv2.GaussianBlur(frame, (21, 21), 0)

                # Subtract the blurred frame from the original frame to get a high-pass filter effect
                high_pass = cv2.subtract(frame, blurred)

                # Acquire thermal data from FLIR camera
                thermal_data = acquire_thermal_data(flir_camera)

                # Process thermal data as needed
                # Example: Display thermal data
                print("Thermal Data:", thermal_data)

                # Display the high-pass filter result
                cv2.imshow('High-Pass Filter Result', high_pass)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print("Frame is not received correctly. Exiting...")
                break
    finally:
        # Release resources
        flir_camera.EndAcquisition()
        flir_camera.DeInit()
        del flir_camera
        system.ReleaseInstance()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

