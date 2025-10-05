import cv2
import numpy
import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Grega\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def draw_label(img, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.9, color=(0, 255, 255), thick=2):
    """
    Draws a high-contrast label: a filled black rectangle with the text on top.
    """
    (tw, th), base = cv2.getTextSize(text, font, scale, thick)
    x, y = org
    # background rectangle (padding 6 px)
    cv2.rectangle(img, (x - 6, y - th - 6), (x + tw + 6, y + base + 6), (0, 0, 0), -1)
    # the text itself
    cv2.putText(img, text, (x, y), font, scale, color, thick, cv2.LINE_AA)

# Define region of interest (ROI)

ROI_X = 300 #left edge = px from left
ROI_Y = 70 #top edge = px from top
ROI_W = 200 #rect width in px
ROI_H = 60 #rect height in px

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
    
    # OCR and FPS controls
    ocrIntervalSeconds = 0.2
    lastOcrTime = 0.0
    lastOcrText = ""
    tesseractConfig = r"--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789.-, -c load_system_dawg=0 -c load_freq_dawg=0"
    fps = 0.0
    frameCount = 0
    fpsTimer = time.time()
    
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
        
        addBlurToRoi = cv2.GaussianBlur(grayForThreshold, (5, 5), 0)
        
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
            
        now = time.time()
        if now - lastOcrTime >= ocrIntervalSeconds:
            try:
                ocr_img = preprocessed
                
                if ocr_img.mean() < 127:
                    ocr_img = cv2.bitwise_not(ocr_img)
                    
                ocr_img = cv2.morphologyEx(ocr_img, cv2.MORPH_OPEN, numpy.ones((2,2), numpy.uint8), iterations=1)
                ocr_img = cv2.morphologyEx(ocr_img, cv2.MORPH_CLOSE, numpy.ones((2,2), numpy.uint8), iterations=1)

                ocr_img = cv2.resize(ocr_img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LINEAR)
                
                text = pytesseract.image_to_string(ocr_img, config=tesseractConfig).strip()
                
                print("OCR raw   :", repr(text))
                
                if text:
                    lastOcrText = text
            except Exception as e:
                lastOcrText = f"[OCR error: {e}]"
                print(lastOcrText)
                
            lastOcrTime = now
            
            pre_disp = preprocessed.copy()
            # If single-channel, convert to BGR so colored label works
            if len(pre_disp.shape) == 2:
                pre_disp = cv2.cvtColor(pre_disp, cv2.COLOR_GRAY2BGR)
            draw_label(pre_disp, f"OCR: {lastOcrText or '(empty)'}", (10, 28))
            cv2.imshow("Webcam OCR - Preprocessed ROI", pre_disp)
            
            #print("OCR raw   :", repr(text))  # show hidden chars like \n
            #print("OCR clean :", repr(lastOcrText))
        
        frameCount += 1
        elapsed = now - fpsTimer
        if elapsed >= 1.0:
            fps = frameCount / elapsed
            frameCount = 0
            fpsTimer = now
        
        hud = (
            f"Mode:{mode} "
            f"Thr:{simpleThreshold if mode==5 else '-'} "
            f"CLAHE:{'on' if useLocalContrastEqualization else 'off'} "
            f"Morph:{'on' if useMorphologyToggle else 'off'} "
            f"FPS:{fps:.1f}"
        )
        draw_label(frame, hud, (10, 28), scale=0.65, color=(50, 220, 50), thick=2)

        draw_label(frame, f"OCR: {lastOcrText or '(empty)'}", (x1, max(30, y1 - 10)))

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