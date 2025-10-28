import cv2


def draw_label(img, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.9, color=(0, 255, 255), thick=2):
    """
    Draws a high-contrast label: a filled black rectangle with the text on top.
    """
    (tw, th), base = cv2.getTextSize(text, font, scale, thick)
    x, y = org
    cv2.rectangle(img, (x - 6, y - th - 6), (x + tw + 6, y + base + 6), (0, 0, 0), -1)
    cv2.putText(img, text, (x, y), font, scale, color, thick, cv2.LINE_AA)


def draw_overlays(frame, roi_coordinates, roi_cropped, binary_image, last_ocr_text, mode, psm, simple_threshold, is_clahe_enabled, is_morphology_enabled, fps, is_saving, save_interval):
    """
    Draws all the text and rectangles on the main frame.
    """
    frame_height = frame.shape[0]
    
    if roi_coordinates:
        x, y, w, h = roi_coordinates
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        draw_label(frame, f"OCR: {last_ocr_text or '(empty)'}", (x, max(30, y - 10)))
        
        if roi_cropped is not None:
            cv2.imshow("Webcam OCR - ROI", roi_cropped)
        if binary_image is not None:
            processed_display = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
            draw_label(processed_display, f"OCR: {last_ocr_text or '(empty)'}", (10, 28))
            cv2.imshow("Webcam OCR - Preprocessed ROI", processed_display)
            
    else:
        draw_label(frame, "Press 'S' to select an ROI", (50, frame_height - 60), scale=0.5)
    
    save_status = f"SAVING ({save_interval}s)" if is_saving else "IDLE"
    save_color = (0, 255, 255) if is_saving else (50, 220, 50)
    
    hud = (
        f"Mode:{mode} "
        f"PSM: {psm} "
        f"Thr:{simple_threshold if mode==5 else '-'} "
        f"CLAHE:{'on' if is_clahe_enabled else 'off'} "
        f"Morph:{'on' if is_morphology_enabled else 'off'} "
        f"FPS:{fps:.1f} | {save_status}"
    )
    
    draw_label(frame, hud, (10, frame_height - 20), scale=0.5, color=save_color, thick=2)
    