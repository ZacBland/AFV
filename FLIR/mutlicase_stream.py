from onvif import ONVIFCamera
import cv2
rtsp_url = "rtsp://admin:qzIRge@10.42.0.45/avc/"
cap = cv2.VideoCapture(rtsp_url)

rtsp_url2 = "rtsp://admin:qzIRge@10.42.0.45/mpeg4/ch1"
cap2 = cv2.VideoCapture(rtsp_url2)


if not cap.isOpened():
    print("Error: Could not open video stream.")
else:
    while True:
        ret, frame = cap.read()
        if ret:
            
            cv2.imshow('ONVIF Camera Stream')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Frame is not received correctly. Exiting...")
            break

cap.release()
cv2.destroyAllWindows()