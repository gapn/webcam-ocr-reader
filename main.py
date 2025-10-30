import cv2
import time
import pytesseract
import os
import sys

import config
from image_processing import process_image
from ocr import perform_ocr
from excel_logging import initiate_excel, write_to_excel
from ui_drawing import draw_overlays
from input_handling import handle_input


def setup_tesseract() -> None:
    """Points pytesseract to Tesseract executable.
    Especially important for aplications packaged with PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        tesseract_path = os.path.join(
            sys._MEIPASS, 'Tesseract-OCR', 'tesseract.exe'
        )
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


def main() -> None:
    """Runs main aplication loop.

    Initializes all state, opens webcam, loops forever, processes frames, handles
    inputs, draws overlays.

    Glossary:
      - ROI: Region of Interest. The box you draw on the screen.
      - OCR: Optical Character Recognition. The process of reading text from an image.
      - PSM: Page Segmentation Mode. A Tesseract setting for how it views the image.
      - CLAHE: Contrast Limited Adaptive Histogram Equalization. An algorithm to improve image contrast.
      - FPS: Frames Per Second.
    
    Raises:
        RuntimeError: If webcam specified by 'CAMERA_INDEX' in config.py
                      cannot be opened.
    """    
    setup_tesseract()

    # --- Initialization ---
    video_capture = cv2.VideoCapture(config.CAMERA_INDEX)
    if not video_capture.isOpened():
        raise RuntimeError(
            f"Could not open webcam index {config.CAMERA_INDEX}."
            "Try different index in config.py"
        )

    initiate_excel(config.EXCEL_FILENAME)

    clahe = cv2.createCLAHE(
        clipLimit=config.CLAHE_CLIP_LIMIT, 
        tileGridSize=config.CLAHE_TILE_GRID_SIZE,
    )

    roi_coordinates = None
    
    # --- Loop parameters ---
    mode = config.DEFAULT_MODE
    simple_threshold = config.DEFAULT_SIMPLE_THRESHOLD
    scale = config.DEFAULT_SCALE
    psm = config.DEFAULT_PSM
    is_clahe_enabled = config.IS_CLAHE_ENABLED
    is_morphology_enabled = config.IS_MORPHOLOGY_ENABLED
    is_saving = config.IS_SAVING_ENABLED
    save_interval = config.DEFAULT_SAVE_INTERVAL_SECONDS
    
    # --- OCR and FPS controls ---
    last_ocr_time = 0.0
    last_save_time = 0.0
    last_ocr_text = config.DEFAULT_LAST_OCR_TEXT
    fps = config.DEFAULT_FPS
    frame_count = config.DEFAULT_FRAME_COUNT
    fps_timer = time.time()
    
    # --- Main loop ---
    while True:
        is_frame_read, frame = video_capture.read()
        now = time.time()
        
        if not is_frame_read:
            print("Error: Could not read frame from camera.", file=sys.stderr)
            break

        roi_cropped = None
        binary_image = None
        
        if roi_coordinates:
            x, y, w, h = roi_coordinates
            roi_cropped = frame[y : y + h, x : x + w]
        
            binary_image = process_image(
                roi_cropped,
                scale,
                is_clahe_enabled,
                clahe,
                mode,
                simple_threshold,
                is_morphology_enabled,
            )
                
            if binary_image is not None and \
            (now - last_ocr_time >= config.OCR_INTERVAL_SECONDS):
                new_ocr_text, _ = perform_ocr(binary_image, psm)

                if new_ocr_text:
                    last_ocr_text = new_ocr_text
                    
                last_ocr_time = now
            
            if is_saving and last_ocr_text and \
            (now - last_save_time) >= save_interval:
                if write_to_excel(last_ocr_text, config.EXCEL_FILENAME):
                    last_save_time = now
        
        frame_count += 1
        elapsed = now - fps_timer
        if elapsed >= config.FPS_CALCULATION_INTERVAL_SECONDS:
            fps = frame_count / elapsed
            frame_count = 0
            fps_timer = now
            
        draw_overlays(
            frame,
            roi_coordinates,
            roi_cropped,
            binary_image,
            last_ocr_text,
            mode,
            psm,
            simple_threshold,
            is_clahe_enabled,
            is_morphology_enabled,
            fps,
            is_saving,
            save_interval,
        )

        cv2.imshow("Webcam OCR - Live", frame)
        
        key_pressed = cv2.waitKey(1) & 0xFF
        (
            should_quit,
            roi_coordinates,
            mode,
            simple_threshold,
            scale,
            psm,
            is_clahe_enabled,
            is_morphology_enabled,
            is_saving,
            save_interval,
        ) = handle_input(
            key_pressed,
            frame,
            roi_coordinates,
            mode,
            simple_threshold,
            scale,
            psm,
            is_clahe_enabled,
            is_morphology_enabled,
            is_saving,
            save_interval,
        )

        if should_quit:
            break
    
    # --- Cleanup ---
    print("Closing application...")
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

