import cv2
import numpy
import time
import pytesseract
import re

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

def extract_number(text):
    """
    Uses regex to find the first valid number in a string.
    """
    if not text:
        return None
    
    # Pattern to find numbers (including negative and decimal)
    pattern = r'\s*[-]?\d+[.,]?\d*'
    match = re.search(pattern, text)
    
    if match:
        # Normalize comma to dot and return the found number string
        return match.group(0).strip().replace(',', '.')
    return None 

def main() -> None:
    """
    Open default webcam, draw ROI rect on live feed and show full frame and cropped ROI in separate windows.
    Press 'q' to quit.
    """
    
    videoCapture = cv2.VideoCapture(0)
    
    roi_coords = None
    
    if not videoCapture.isOpened():
        raise RuntimeError("Could not open webcam (index 0). Try different index: 1, 2, ...")
    
    # Loop paramethers
    mode = 3
    simpleThreshold = 100
    scale = 2.5
    psm = 7
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
        now = time.time()
        
        if not frameRead:
            break
        
        if roi_coords:
            # An ROI has been selected, so we process it
            x, y, w, h = roi_coords
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            draw_label(frame, f"OCR: {lastOcrText or '(empty)'}", (x, max(30, y - 10)))
            croppedRoi = frame[y:y+h, x:x+w]
        
        
            # Preprocessing
            
            convertRoiToGrey = cv2.cvtColor(croppedRoi, cv2.COLOR_BGR2GRAY)
            
            if convertRoiToGrey.shape[0] > 0 and convertRoiToGrey.shape[1] > 0:
                greyScaled = cv2.resize(convertRoiToGrey, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            else:
                continue
            
            denoised = cv2.fastNlMeansDenoising(greyScaled, h=10)
            blurred = cv2.GaussianBlur(denoised, (3, 3), 0)
            kernel_sharp = numpy.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(blurred, -1, kernel_sharp)
            
            if useLocalContrastEqualization:
                sharpened = localContrastEqualization.apply(sharpened)
            
            grad_x = cv2.Sobel(sharpened, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(sharpened, cv2.CV_64F, 0, 1, ksize=3)
            gradient = numpy.sqrt(grad_x**2 + grad_y**2)
            gradient = numpy.uint8(gradient / gradient.max() * 255)
            
            enhancedImage = cv2.addWeighted(sharpened, 0.8, gradient, 0.2, 0)            
            
            #Thresholding modes
            if mode == 1:
                _, preprocessed = cv2.threshold(enhancedImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            elif mode == 2:
                _, preprocessed = cv2.threshold(enhancedImage, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            elif mode == 3:
                preprocessed = cv2.adaptiveThreshold(
                    enhancedImage, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    21,
                    10
                )
            elif mode == 4:
                preprocessed = cv2.adaptiveThreshold(
                    enhancedImage, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    21,
                    10
                )
            else:
                _, preprocessed = cv2.threshold(enhancedImage, simpleThreshold, 255, cv2.THRESH_BINARY)
            
            if useMorphologyToggle:
                kernel = numpy.ones((3, 3), numpy.uint8)
                preprocessed = cv2.dilate(preprocessed, kernel, iterations=1)
                
            
            if now - lastOcrTime >= ocrIntervalSeconds:
                try:
                    ocr_img = preprocessed
                    if ocr_img is None:
                        continue
                    
                    if ocr_img.mean() < 127:
                        ocr_img = cv2.bitwise_not(ocr_img)
                        
                    baseConfiguration = r'--oem 1 -c tessedit_char_whitelist=0123456789.-, -c load_system_dawg=0 -c load_freq_dawg=0'
                    
                    configurations = [
                        f'--psm {psm} {baseConfiguration}',
                        f'--psm 7 {baseConfiguration}', #default
                        f'--psm 8 {baseConfiguration}', #single word
                        f'--psm 13 {baseConfiguration}', #raw line
                    ]

                    bestText = ""
                    for configuration in configurations:
                        text = pytesseract.image_to_string(ocr_img, config=configuration).strip()
                        if len(text) > len(bestText):
                            bestText = text
                    
                    print("OCR raw    :", repr(bestText))
                    
                    cleaned_text = extract_number(bestText)
                    print("OCR clean  :", repr(cleaned_text))

                    if cleaned_text:
                        lastOcrText = cleaned_text
                        
                except Exception as e:
                    lastOcrText = f"[OCR error: {e}]"
                    print(lastOcrText)
                    
                lastOcrTime = now
            cv2.imshow("Webcam OCR - ROI", croppedRoi)
            
        
            pre_disp = preprocessed.copy()
            # If single-channel, convert to BGR so colored label works
            if len(pre_disp.shape) == 2:
                pre_disp = cv2.cvtColor(pre_disp, cv2.COLOR_GRAY2BGR)
            draw_label(pre_disp, f"OCR: {lastOcrText or '(empty)'}", (10, 28))
            cv2.imshow("Webcam OCR - Preprocessed ROI", pre_disp)
        else:
        # No ROI selected yet, so we prompt the user
            draw_label(frame, "Press 'S' to select an ROI", (50, 70), scale=0.8)
            croppedRoi = None
        
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

        

        # Video views
        
        cv2.imshow("Webcam OCR - Live", frame)
        
        
        keyPress = cv2.waitKey(1) & 0xFF
        if keyPress == ord('q'):
            break
        elif keyPress == ord('s'):
            print("Select an ROI and press SPACE or ENTER")
            selection = cv2.selectROI("Webcam OCR - Live", frame, fromCenter=False, showCrosshair=True)
            if selection[2] > 0 and selection[3] > 0:
                roi_coords = selection
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
        elif keyPress in (ord('+'), ord('=')):
            scale = min(8.0, scale + 0.5)
            print(f"Scale set to: {scale}")
        elif keyPress in (ord('-'), ord('_')):
            scale = max(1.0, scale - 0.5)
            print(f"Scale set to: {scale}")
        elif keyPress == ord('p'):
            psms = [7, 8, 13, 6] # Common PSM modes for this task
            current_index = psms.index(psm) if psm in psms else 0
            psm = psms[(current_index + 1) % len(psms)]
            print(f"PSM set to: {psm}")
        
    videoCapture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()