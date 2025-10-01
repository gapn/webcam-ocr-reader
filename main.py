import cv2

# Define region of interest (ROI)

ROI_X = 100 #left edge = px from left
ROI_Y = 100 #top edge = px from top
ROI_W = 100 #rect width in px
ROI_H = 100 #rect height in px

def main() -> None:
    """
    Open default webcam, draw ROI rect on live feed and show full frame and cropped ROI in separate windows.
    Press 'q' to quit.
    """
    
    videoCapture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not videoCapture.isOpened():
        raise RuntimeError("Could not open webcam (index 0). Try different index: 1, 2, ...")
    
    while True:
        frameRead, frame = videoCapture.read()
        
        if not frameRead:
            break
        
        x1, y1 = ROI_X, ROI_Y
        x2, y2 = ROI_X + ROI_W, ROI_Y + ROI_H
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        croppedRoi = frame[y1:y2, x1:x2]
        
        cv2.imshow("Webcam OCR - Live", frame)
        cv2.imshow("Webcam OCR - ROI", croppedRoi)
        
        keyPress = cv2.waitKey(1) & 0xFF
        if keyPress == ord('q'):
            break
        
    videoCapture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
        
        