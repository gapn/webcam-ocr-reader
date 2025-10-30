import cv2
import numpy as np
from typing import Tuple, Optional


# --- Constants ---
ROI_WINDOW_NAME = "Webcam OCR - Live"

# Threshold Controls
THRESH_STEP = 5
THRESH_MIN = 0
THRESH_MAX = 255

# Scale Controls
SCALE_STEP = 0.5
SCALE_MIN = 1.0
SCALE_MAX = 8.0

# PSM Controls
PSM_MODES = [7, 8, 13, 6]

# Save Interval Controls
SAVE_INTERVAL_STEP = 0.5
SAVE_INTERVAL_MIN = 0.5
SAVE_INTERVAL_MAX = 3600.0

# --- Type Aliases ---
ROI_Coordinates = Optional[Tuple[int, int, int, int]]

HandleInputReturn = Tuple[
    bool,
    ROI_Coordinates,
    int,
    int,
    float,
    int,
    bool,
    bool,
    bool,
    float,
]
def handle_input(
    key_pressed: int,
    frame: np.ndarray,
    roi_coordinates: ROI_Coordinates,
    mode: int,
    simple_threshold: int,
    scale: float,
    psm: int,
    is_clahe_enabled: bool,
    is_morphology_enabled: bool,
    is_saving: bool,
    save_interval: float,
) -> HandleInputReturn:
    """Handles all keyboard inputs and returns the updated application state.
    This function does not modify the state directly, but returns new state
    tuple based on the input.

    Args:
        key_pressed (int): (0xFF & cv2.waitKey(1)) value.
        frame (np.ndarray): Current camera frame, needed for cv2.selectROI.
        roi_coordinates (ROI_Coordinates): Current (x, y, w, h) or None.
        mode (int): Current thresholding mode.
        simple_threshold (int): Current simple threshold value.
        scale (float): Current image processing scale.
        psm (int): Current Tesseract PSM.
        is_clahe_enabled (bool): Current CLAHE flag.
        is_morphology_enabled (bool): Current morphology flag.
        is_saving (bool): Current saving flag.
        save_interval (float): Current save interval in seconds.

    Returns:
        HandleInputReturn: Tuple containing new state.
    """
    should_quit = False
    
    if key_pressed == ord('q'):
        should_quit = True
    
    elif key_pressed == ord('s'):
        print("Select an ROI and press SPACE or ENTER")
        selection = cv2.selectROI(
            ROI_WINDOW_NAME, frame, fromCenter=False, showCrosshair=True
        )
        if selection[2] > 0 and selection[3] > 0:
            roi_coordinates = selection

    elif key_pressed == ord('1'):
        mode = 1
    elif key_pressed == ord('2'):
        mode = 2
    elif key_pressed == ord('3'):
        mode = 3
    elif key_pressed == ord('4'):
        mode = 4
    elif key_pressed == ord('5'):
        mode = 5

    elif key_pressed == ord('['):
        simple_threshold = max(THRESH_MIN, simple_threshold - THRESH_STEP)
        print(f"Threshold set to: {simple_threshold}")
    elif key_pressed == ord(']'):
        simple_threshold = min(THRESH_MAX, simple_threshold + THRESH_STEP)
        print(f"Threshold set to: {simple_threshold}")

    elif key_pressed == ord('c'):
        is_clahe_enabled = not is_clahe_enabled
        print(f"CLAHE toggled {'ON' if is_clahe_enabled else 'OFF'}")
    elif key_pressed == ord('m'):
        is_morphology_enabled = not is_morphology_enabled
        print(f"Morphology toggled {'ON' if is_clahe_enabled else 'OFF'}")

    elif key_pressed in (ord('+'), ord('=')):
        scale = min(SCALE_MAX, scale + SCALE_STEP)
        print(f"Scale set to: {scale}")
    elif key_pressed in (ord('-'), ord('_')):
        scale = max(SCALE_MIN, scale - SCALE_STEP)
        print(f"Scale set to: {scale}")

    elif key_pressed == ord('p'):
        try:
            current_index = PSM_MODES.index(psm)
        except ValueError:
            current_index = 0
        psm = PSM_MODES[(current_index + 1) % len(PSM_MODES)]
        print(f"PSM set to: {psm}")

    elif key_pressed == ord('w'):
        is_saving = not is_saving
        print(f"Saving toggled {'ON' if is_saving else 'OFF'}")

    elif key_pressed == ord(','):
        save_interval = max(SAVE_INTERVAL_MIN, save_interval - SAVE_INTERVAL_STEP)
        print(f"Save interval set to: {save_interval}s")
    elif key_pressed == ord('.'):
        save_interval = min(SAVE_INTERVAL_MAX, save_interval + SAVE_INTERVAL_STEP)
        print(f"Save interval set to: {save_interval}s")

    return (
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
    )
