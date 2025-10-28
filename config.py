"""Global configuration file for Webcam OCR application

Stores all default parameters and 'magic' numbers in one central location
"""


# --- Image Processing Parameters ---
DEFAULT_MODE = 1
DEFAULT_SIMPLE_THRESHOLD = 100
DEFAULT_SCALE = 2.5
DEFAULT_PSM = 7
IS_CLAHE_ENABLED = True
IS_MORPHOLOGY_ENABLED = False


# --- Saving Parameters ---
IS_SAVING_ENABLED = False
DEFAULT_SAVE_INTERVAL_SECONDS = 5.0
EXCEL_FILENAME = "measurements.xlsx"


# --- Performance & State Parameters ---
OCR_INTERVAL_SECONDS = 0.2
FPS_CALCULATION_INTERVAL_SECONDS = 1.0
DEFAULT_FPS = 0.0
DEFAULT_FRAME_COUNT = 0
DEFAULT_LAST_OCR_TEXT = ""

