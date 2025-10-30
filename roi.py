import numpy as np
from typing import Optional, Tuple


Rect = Tuple[int, int, int, int]


class ROI:
    """Class to store all data for a single Region of Interest
    
    Acts as container for ROI's configuration (position) and its current
    runtime state (latest image and text).
    """
    def __init__(self, rect: Rect, name: str):
        """Initializes new ROI object

        Args:
            rect (Rect): Bounding box of ROI as tuple (x, y, w, h)
            name (str): Display name for this ROI (eg. ROI temp, ROI humid, ...)
        """
        self.rect: Rect = rect
        self.name: str = name

        self.last_text: str = ""
        self.raw_text: Optional[str] = None
        self.processed_image: Optional[np.ndarray] = None
        self.cropped_image: Optional[np.ndarray] = None
    
