import cv2
import pytesseract
import re
import numpy as np
import sys


# --- Constants ---
NUMBER_REGEX_PATTERN = r'\s*[-]?\d+[.,]?\d*'
TESSERACT_BASE_CONFIG = r'--oem 1 -c tessedit_char_whitelist=0123456789.-, \
                        -c load_system_dawg=0 -c load_freq_dawg=0'
INVERT_THRESHOLD = 127.0
    

def extract_number(text: str | None) -> str | None:
    """Uses regex to find the first valid number in a string.
    
    Args:
        text (str | None): Raw string from OCR, or None.

    Returns:
        str | None: Cleaned string of the first number found, or None.
    """
    if not text:
        return None
    
    match = re.search(NUMBER_REGEX_PATTERN, text)
    
    if match:
        return match.group(0).strip().replace(',', '.')
    return None 


def perform_ocr(image: np.ndarray | None, psm: int) -> tuple[str | None, str | None]:
    """Performs multi-configuration OCR on a binary image and returns the cleaned 
    number.
    
    Args:
        image (np.ndarray | None): Preprocessed binary image to read.
        psm (int): User's currently selected Tesseract PSM mode.

    Returns:
        tuple[str | None, str | None]:
            - Cleaned number string (or None if not found).
            - Best raw text found (or None if OCR failed).
    """
    if image is None:
        return None, None
    
    if image.mean() < INVERT_THRESHOLD:
        image = cv2.bitwise_not(image)
    
    psm_modes_to_try = list(dict.fromkeys([
        psm, #users choice first
        7, #single text line
        8, #single word
        13, #raw line
    ]))
    
    configurations = [
        f'--psm {mode} {TESSERACT_BASE_CONFIG}' for mode in psm_modes_to_try
    ]

    best_ocr_text: str | None = None
    best_text_len = -1 #allow empty string as valid result

    for configuration in configurations:
        try:
            text = pytesseract.image_to_string(image, config=configuration).strip()
            if len(text) > best_text_len:
                best_ocr_text = text
                best_text_len = len(text)
        except Exception as e:
            print(f"[Tesseract Error]: {e}", file=sys.stderr)
            continue
    
    cleaned_ocr_text = extract_number(best_ocr_text)
    return cleaned_ocr_text, best_ocr_text

