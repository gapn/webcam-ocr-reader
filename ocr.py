import cv2
import pytesseract
import re


def extract_number(text):
    """
    Uses regex to find the first valid number in a string.
    """
    if not text:
        return None
    
    pattern = r'\s*[-]?\d+[.,]?\d*'
    match = re.search(pattern, text)
    
    if match:
        return match.group(0).strip().replace(',', '.')
    return None 


def perform_ocr(image, psm, extract_number_function):
    """
    Performs multi-configuration OCR on a binary image and returns the cleaned number.
    """
    if image is None:
        return None, None
    
    if image.mean() < 127:
        image = cv2.bitwise_not(image)
        
    base_configuration = r'--oem 1 -c tessedit_char_whitelist=0123456789.-, -c load_system_dawg=0 -c load_freq_dawg=0'
    
    configurations = [
        f'--psm {psm} {base_configuration}',
        f'--psm 7 {base_configuration}', #default
        f'--psm 8 {base_configuration}', #single word
        f'--psm 13 {base_configuration}', #raw line
    ]

    best_ocr_text = ""
    for configuration in configurations:
        try:
            text = pytesseract.image_to_string(image, config=configuration).strip()
            if len(text) > len(best_ocr_text):
                best_ocr_text = text
        except Exception as e:
            print(f"[Tesseract Error]: {e}")
            continue
    
    cleaned_ocr_text = extract_number_function(best_ocr_text)
    return cleaned_ocr_text, best_ocr_text

