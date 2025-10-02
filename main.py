import cv2
import numpy
# Define region of interest (ROI)

ROI_X = 10 #left edge = px from left
ROI_Y = 10 #top edge = px from top
ROI_W = 300 #rect width in px
ROI_H = 300 #rect height in px

def main() -> None:
    """
    Open default webcam, draw ROI rect on live feed and show full frame and cropped ROI in separate windows.
    Press 'q' to quit.
    """
    
    videoCapture = cv2.VideoCapture(0)
    
    if not videoCapture.isOpened():
        raise RuntimeError("Could not open webcam (index 0). Try different index: 1, 2, ...")
    
    # Loop paramethers
    mode = 3
    simpleThreshold = 150
    useLocalContrastEqualization = True
    useMorphologyToggle = False
    
    localContrastEqualization = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    while True:
        frameRead, frame = videoCapture.read()
        
        if not frameRead:
            break
        
        x1, y1 = ROI_X, ROI_Y
        x2, y2 = ROI_X + ROI_W, ROI_Y + ROI_H
        
        h, w = frame.shape[:2]
        x1 = max(0, min(x1, w - 1)); x2 = max(0, min(x2, w))
        y1 = max(0, min(y1, h - 1)); y2 = max(0, min(y2, h))
        if x2 <= x1 or y2 <= y1:
            cv2.putText(frame, "ROI out of bounds", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.imshow("Webcam OCR - Live", frame)
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break
            continue       
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        croppedRoi = frame[y1:y2, x1:x2]
        
        # Preprocessing
        
        convertRoiToGrey = cv2.cvtColor(croppedRoi, cv2.COLOR_BGR2GRAY)
        
        if useLocalContrastEqualization:
            grayForThreshold = localContrastEqualization.apply(convertRoiToGrey)
        else:
            grayForThreshold = convertRoiToGrey
        
        addBlurToRoi = cv2.GaussianBlur(grayForThreshold, (5, 5), 0) #if text very noisy, change 5,5 to 7,7
        
        #Thresholding modes
        if mode == 1:
            _, preprocessed = cv2.threshold(addBlurToRoi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif mode == 2:
            _, preprocessed = cv2.threshold(addBlurToRoi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        elif mode == 3:
            preprocessed = cv2.adaptiveThreshold(
                addBlurToRoi, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                21,
                10
            )
        elif mode == 4:
            preprocessed = cv2.adaptiveThreshold(
                addBlurToRoi, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                21,
                10
            )
        else:
            _, preprocessed = cv2.threshold(addBlurToRoi, simpleThreshold, 255, cv2.THRESH_BINARY)
        
        if useMorphologyToggle:
            kernel = numpy.ones((3, 3), numpy.uint8)
            preprocessed = cv2.dilate(preprocessed, kernel, iterations=1)
        
        # Video views
        
        cv2.imshow("Webcam OCR - Live", frame)
        cv2.imshow("Webcam OCR - ROI", croppedRoi)
        cv2.imshow("Webcam OCR - Preprocessed ROI", preprocessed)
        
        keyPress = cv2.waitKey(1) & 0xFF
        if keyPress == ord('q'):
            break
        elif keyPress == ord('1'):
            mode = 1
        elif keyPress == ord('2'):
            mode = 2
        elif keyPress == ord('3'):
            mode = 3
        elif keyPress == ord('4'):
            mode = 4
        elif keyPress == ord('5'):
            mode = 5
        elif keyPress == ord('['):
            simpleThreshold = max(0, simpleThreshold - 5)
        elif keyPress == ord(']'):
            simpleThreshold = min(255, simpleThreshold + 5)
        elif keyPress == ord('c'):
            useLocalContrastEqualization = not useLocalContrastEqualization
        elif keyPress == ord('m'):
            useMorphologyToggle = not useMorphologyToggle
        
    videoCapture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
        
        