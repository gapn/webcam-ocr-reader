import cv2
import numpy


def process_image(image, scale, is_clahe_enabled, clahe, mode, simple_threshold):
    """
    Applies the full 'scale-first' image processing pipeline to an image.
    """
    roi_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
    if roi_gray.shape[0] == 0 or roi_gray.shape[1] == 0:
        return None
    gray_scaled = cv2.resize(roi_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    denoised = cv2.fastNlMeansDenoising(gray_scaled, h=10)
    blurred = cv2.GaussianBlur(denoised, (3, 3), 0)
    kernel_sharp = numpy.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(blurred, -1, kernel_sharp)
    
    if is_clahe_enabled:
        sharpened = clahe.apply(sharpened)
    
    gradient_x = cv2.Sobel(sharpened, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(sharpened, cv2.CV_64F, 0, 1, ksize=3)
    gradient = numpy.sqrt(gradient_x**2 + gradient_y**2)
    gradient = numpy.uint8(gradient / gradient.max() * 255)
    
    enhanced_image = cv2.addWeighted(sharpened, 0.8, gradient, 0.2, 0)            
    
    if mode == 1:
        _, binary_image = cv2.threshold(enhanced_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif mode == 2:
        _, binary_image = cv2.threshold(enhanced_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    elif mode == 3:
        binary_image = cv2.adaptiveThreshold(
            enhanced_image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            21,
            10
        )
    elif mode == 4:
        binary_image = cv2.adaptiveThreshold(
            enhanced_image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            21,
            10
        )
    else:
        _, binary_image = cv2.threshold(enhanced_image, simple_threshold, 255, cv2.THRESH_BINARY)
        
    return binary_image

