import cv2


def handle_input(key_pressed, frame, roi_coordinates, mode, simple_threshold, scale, psm, is_clahe_enabled, is_morphology_enabled, is_saving, save_interval):
    """
    Handles all keyboard inputs and returns the updated state.
    """
    should_quit = False
    
    if key_pressed == ord('q'):
        should_quit = True
    elif key_pressed == ord('s'):
        print("Select an ROI and press SPACE or ENTER")
        selection = cv2.selectROI("Webcam OCR - Live", frame, fromCenter=False, showCrosshair=True)
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
        simple_threshold = max(0, simple_threshold - 5)
    elif key_pressed == ord(']'):
        simple_threshold = min(255, simple_threshold + 5)
    elif key_pressed == ord('c'):
        is_clahe_enabled = not is_clahe_enabled
    elif key_pressed == ord('m'):
        is_morphology_enabled = not is_morphology_enabled
    elif key_pressed in (ord('+'), ord('=')):
        scale = min(8.0, scale + 0.5)
        print(f"Scale set to: {scale}")
    elif key_pressed in (ord('-'), ord('_')):
        scale = max(1.0, scale - 0.5)
        print(f"Scale set to: {scale}")
    elif key_pressed == ord('p'):
        psms = [7, 8, 13, 6]
        current_index = psms.index(psm) if psm in psms else 0
        psm = psms[(current_index + 1) % len(psms)]
        print(f"PSM set to: {psm}")
    elif key_pressed == ord('w'):
        is_saving = not is_saving
        print(f"Saving toggled {'ON' if is_saving else 'OFF'}")
    elif key_pressed == ord(','):
        save_interval = max(0.5, save_interval - 0.5)
        print(f"Save interval set to: {save_interval}s")
    elif key_pressed == ord('.'):
        save_interval = min(3600.0, save_interval + 0.5)
        print(f"Save interval set to: {save_interval}s")
    return should_quit, roi_coordinates, mode, simple_threshold, scale, psm, is_clahe_enabled, is_morphology_enabled, is_saving, save_interval
