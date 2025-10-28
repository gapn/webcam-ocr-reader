import cv2
import time
import pytesseract
import os
import sys

import config
from image_processing import process_image
from ocr import perform_ocr, extract_number
from excel_logging import initiate_excel, write_to_excel
from ui_drawing import draw_overlays
from input_handling import handle_input


def setup_tesseract():
    if getattr(sys, 'frozen', False):
        tesseract_path = os.path.join(sys._MEIPASS, 'Tesseract-OCR', 'tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

def main() -> None:
    """
    Open default webcam, draw ROI rect on live feed and show full frame and cropped ROI in separate windows.
    Press 'q' to quit.
    Glossary:
      - ROI: Region of Interest. The box you draw on the screen.
      - OCR: Optical Character Recognition. The process of reading text from an image.
      - PSM: Page Segmentation Mode. A Tesseract setting for how it views the image.
      - CLAHE: Contrast Limited Adaptive Histogram Equalization. An algorithm to improve image contrast.
      - FPS: Frames Per Second.
    """
    
    setup_tesseract()

    video_capture = cv2.VideoCapture(1) # <- Chose camera index here
    if not video_capture.isOpened():
        raise RuntimeError("Could not open webcam (index 0). Try different index: 1, 2, ...")

    initiate_excel(config.EXCEL_FILENAME)
    
    roi_coordinates = None
    
   
    # Loop paramethers
    mode = config.DEFAULT_MODE
    simple_threshold = config.DEFAULT_SIMPLE_THRESHOLD
    scale = config.DEFAULT_SCALE
    psm = config.DEFAULT_PSM
    is_clahe_enabled = config.IS_CLAHE_ENABLED
    is_morphology_enabled = config.IS_MORPHOLOGY_ENABLED
    is_saving = config.IS_SAVING_ENABLED
    save_interval = config.DEFAULT_SAVE_INTERVAL_SECONDS
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    # OCR and FPS controls
    ocr_interval_seconds = config.OCR_INTERVAL_SECONDS
    lat_ocr_time = 0.0
    last_save_time = 0.0
    last_ocr_text = ""
    fps = 0.0
    frame_count = 0
    fps_timer = time.time()
    
    while True:
        is_frame_read, frame = video_capture.read()
        now = time.time()
        
        if not is_frame_read:
            break

        roi_cropped = None
        binary_image = None
        
        if roi_coordinates:
            x, y, w, h = roi_coordinates
            roi_cropped = frame[y:y+h, x:x+w]
        
            binary_image = process_image(
                roi_cropped, scale, is_clahe_enabled, clahe, mode, simple_threshold, is_morphology_enabled
            )
                
            if binary_image is not None and (now - lat_ocr_time >= ocr_interval_seconds):
                new_ocr_text, raw_ocr_text = perform_ocr(binary_image, psm, extract_number)

                if new_ocr_text:
                    last_ocr_text = new_ocr_text
                    
                lat_ocr_time = now
            
            if is_saving and last_ocr_text and (now - last_save_time) >= save_interval:
                if write_to_excel(last_ocr_text, config.EXCEL_FILENAME):
                    last_save_time = now
        
        frame_count += 1
        elapsed = now - fps_timer
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            fps_timer = now
            
        draw_overlays(frame, roi_coordinates, roi_cropped, binary_image, last_ocr_text, mode, psm, simple_threshold, is_clahe_enabled, is_morphology_enabled, fps, is_saving, save_interval)

        cv2.imshow("Webcam OCR - Live", frame)
        
        key_pressed = cv2.waitKey(1) & 0xFF
        should_quit, roi_coordinates, mode, simple_threshold, scale, psm, is_clahe_enabled, is_morphology_enabled, is_saving, save_interval = handle_input(
            key_pressed, frame, roi_coordinates, mode, simple_threshold, scale, psm, is_clahe_enabled, is_morphology_enabled, is_saving, save_interval
        )
        if should_quit:
            break
        
    print("Closing application...")
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()