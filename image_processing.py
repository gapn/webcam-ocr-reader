import cv2
import numpy as np


# --- Pipeline Constants ---
DENOISE_STRENGTH = 10

# --- Blurring ---
GAUSSIAN_BLUR_KERNEL = (3, 3)

# --- Sharpening ---
SHARPEN_KERNEL = np.array([
    [-1, -1, -1],
    [-1, 9, -1],
    [-1, -1, -1]
])

# --- Edge/Gradient Enhancement ---
GRADIENT_WEIGHT = 0.2
SHARPEN_WEIGHT = 0.8

# --- Adaptive Thresholding ---
ADAPTIVE_THRESH_BLOCK_SIZE = 21
ADAPTIVE_THRESH_CONSTANT = 10

# --- Morphology (Dilation) ---
MORPH_KERNEL_SIZE = (3, 3)
MORPH_ITERATIONS = 1


def process_image(
    image: np.ndarray,
    scale: float,
    is_clahe_enabled: bool,
    clahe: cv2.CLAHE,
    mode: int,
    simple_threshold: int,
    is_morphology_enabled: bool,
) -> np.ndarray | None:
    """Applies the full 'scale-first' image processing pipeline to an image.
    
    Args:
        image (np.ndarray): The raw BGR ROI image.
        scale (float): The factor to scale the image by.
        is_clahe_enabled (bool): Flag to enable/disable CLAHE.
        clahe (cv2.CLAHE): The pre-created CLAHE object.
        mode (int): The selected thresholding mode (1-5).
        simple_threshold (int): The threshold value for mode 5.
        is_morphology_enabled (bool): Flag to enable/disable dilation.

    Returns:
        np.ndarray | None: The final processed binary image, or None if input is 
        invalid.
    """
    roi_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
    if roi_gray.shape[0] == 0 or roi_gray.shape[1] == 0:
        return None
    gray_scaled = cv2.resize(
        roi_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
    )
    
    denoised = cv2.fastNlMeansDenoising(gray_scaled, h=DENOISE_STRENGTH)
    blurred = cv2.GaussianBlur(denoised, GAUSSIAN_BLUR_KERNEL, 0)
    sharpened = cv2.filter2D(blurred, -1, SHARPEN_KERNEL)
    
    if is_clahe_enabled:
        sharpened = clahe.apply(sharpened)
    
    gradient_x = cv2.Sobel(sharpened, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(sharpened, cv2.CV_64F, 0, 1, ksize=3)
    gradient = np.sqrt(gradient_x**2 + gradient_y**2)
    gradient = np.uint8(gradient / gradient.max() * 255)
    
    enhanced_image = cv2.addWeighted(
        sharpened, SHARPEN_WEIGHT, gradient, GRADIENT_WEIGHT, 0
    )            
    
    binary_image = None
    if mode == 1:
        _, binary_image = cv2.threshold(enhanced_image, 0, 255, cv2.THRESH_BINARY \
                                        + cv2.THRESH_OTSU)
    elif mode == 2:
        _, binary_image = cv2.threshold(enhanced_image, 0, 255, \
                                        cv2.THRESH_BINARY_INV \
                                        + cv2.THRESH_OTSU)
    elif mode == 3:
        binary_image = cv2.adaptiveThreshold(
            enhanced_image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            ADAPTIVE_THRESH_BLOCK_SIZE,
            ADAPTIVE_THRESH_CONSTANT
        )
    elif mode == 4:
        binary_image = cv2.adaptiveThreshold(
            enhanced_image, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            ADAPTIVE_THRESH_BLOCK_SIZE,
            ADAPTIVE_THRESH_CONSTANT
        )
    else:
        _, binary_image = cv2.threshold(enhanced_image, simple_threshold, 255, \
                                        cv2.THRESH_BINARY)
        
    if is_morphology_enabled: 
        kernel = np.ones(MORPH_KERNEL_SIZE, np.uint8)
        binary_image = cv2.dilate(
            binary_image, kernel, iterations=MORPH_ITERATIONS
        )

    return binary_image

