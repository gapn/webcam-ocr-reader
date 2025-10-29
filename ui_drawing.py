import cv2
import numpy as np


# Styling
COLOR_BLACK = (0, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_GREEN_BRIGHT = (0, 255, 0)
COLOR_GREEN_MUTED = (50, 220, 50)

# Label Drawing
LABEL_FONT = cv2.FONT_HERSHEY_SIMPLEX
LABEL_BG_PADDING = 6
LABEL_THICKNESS = 2
LABEL_DEFAULT_SCALE = 0.9

# HUD Positioning
HUD_POS = (10, -20)
HUD_SCALE = 0.5
ROI_PROMPT_POS = (50, -60)
ROI_PROMPT_SCALE = 0.5
OCR_LABEL_OFFSET_Y = -10
OCR_LABEL_MIN_Y = 30
DEBUG_LABEL_POS = (10, 28)


def draw_label(
        img: np.ndarray,
        text: str,
        position: tuple[int, int],
        font: int = LABEL_FONT,
        scale: float = LABEL_DEFAULT_SCALE,
        color: tuple[int, int, int] = COLOR_YELLOW,
        thick: int = LABEL_THICKNESS,
) -> None:
    """Draws a high-contrast label: a filled black rectangle with the text on top.

    Args:
        img (np.ndarray): Image to draw on (modified in-place).
        text (str): Text content to draw.
        position (tuple[int, int]): (x, y) coordinates for the bottom-left corner 
        of the text.
        font (int, optional): OpenCV font type. Defaults to LABEL_FONT.
        scale (float, optional): Font scale. Defaults to LABEL_DEFAULT_SCALE.
        color (tuple[int, int, int], optional): BGR text color. Defaults to 
        COLOR_YELLOW.
        thick (int, optional): Text thickness. Defaults to LABEL_THICKNESS.
    """
    (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thick)
    x, y = position
    cv2.rectangle(
        img,
        (x - LABEL_BG_PADDING, y - text_height - LABEL_BG_PADDING),
        (x + text_width + LABEL_BG_PADDING, y + baseline + LABEL_BG_PADDING),
        COLOR_BLACK,
        -1
    )
    cv2.putText(img, text, (x, y), font, scale, color, thick, cv2.LINE_AA)


def _show_debug_windows(
    roi_cropped: np.ndarray | None,
    binary_image: np.ndarray | None,
    last_ocr_text: str,
) -> None:
    """Handles the creation and drawing for the two debug windows.

    Args:
        roi_cropped (np.ndarray | None): Raw cropped image from the main frame.
        binary_image (np.ndarray | None): Final preprocessed binary image.
        last_ocr_text (str): Most recent valid OCR text to display.
    """
    if roi_cropped is not None:
        cv2.imshow("Webcam OCR - ROI", roi_cropped)
    if binary_image is not None:
        processed_display = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        draw_label(
            processed_display,
            f"OCR: {last_ocr_text or '(empty)'}",
            DEBUG_LABEL_POS,
        )
        cv2.imshow("Webcam OCR - Preprocessed ROI", processed_display)


def draw_overlays(
    frame: np.ndarray,
    roi_coordinates: tuple[int, int, int, int] | None,
    roi_cropped: np.ndarray | None,
    binary_image: np.ndarray | None,
    last_ocr_text: str,
    mode: int,
    psm: int,
    simple_threshold: int,
    is_clahe_enabled: bool,
    is_morphology_enabled: bool,
    fps: float,
    is_saving: bool,
    save_interval: float,
) -> None:
    """Draws all text, rectangles and debug windows on the main frame.

    Args:
        frame (np.ndarray): Main camera frame to be modified in-place.
        roi_coordinates (tuple[int, int, int, int] | None): (x, y, w, h) of 
        the selected ROI.
        roi_cropped (np.ndarray | None): Raw cropped image from the main 
        frame.
        binary_image (np.ndarray | None): Final preprocessed binary image.
        last_ocr_text (str): Most recent valid OCR text.
        mode (int): Current thresholding mode (1-5).
        psm (int): Current Tesseract PSM value.
        simple_threshold (int): Current simple threshold value (for mode 5).
        is_clahe_enabled (bool): Flag if CLAHE is active.
        is_morphology_enabled (bool): Flag if morphology is active.
        fps (float): Current calculated FPS.
        is_saving (bool): Flag if saving to Excel is active.
        save_interval (float): Current save interval in seconds.
    """
    frame_height = frame.shape[0]
    
    if roi_coordinates:
        x, y, w, h = roi_coordinates
        cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR_GREEN_BRIGHT, 2)
        
        ocr_label_y = max(OCR_LABEL_MIN_Y, y + OCR_LABEL_OFFSET_Y)
        draw_label(frame, f"OCR: {last_ocr_text or '(empty)'}", (x, ocr_label_y))
        
        _show_debug_windows(roi_cropped, binary_image, last_ocr_text)

    else:
        prompt_y = frame_height + ROI_PROMPT_POS[1]
        draw_label(
            frame,
            "Press 'S' to select an ROI",
            (ROI_PROMPT_POS[0], prompt_y),
            scale=ROI_PROMPT_SCALE,
        )
    
    save_status = f"SAVING ({save_interval}s)" if is_saving else "IDLE"
    save_color = COLOR_YELLOW if is_saving else COLOR_GREEN_MUTED
    
    hud = (
        f"Mode:{mode} "
        f"PSM: {psm} "
        f"Thr:{simple_threshold if mode==5 else '-'} "
        f"CLAHE:{'on' if is_clahe_enabled else 'off'} "
        f"Morph:{'on' if is_morphology_enabled else 'off'} "
        f"FPS:{fps:.1f} | {save_status}"
    )

    hud_y = frame_height + HUD_POS[1]
    
    draw_label(
        frame,
        hud,
        (HUD_POS[0], hud_y),
        scale=HUD_SCALE,
        color=save_color,
        thick=LABEL_THICKNESS,
    )

