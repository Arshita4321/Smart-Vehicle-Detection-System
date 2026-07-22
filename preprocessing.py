import cv2
import numpy as np
from PIL import Image

def preprocess_image(image: np.ndarray, apply_blur: bool, resize_dim: tuple = (640, 640)) -> np.ndarray:
    \"\"\"
    Preprocesses the image for YOLO detection.
    \"\"\"
    # Resize image for faster processing
    processed_img = cv2.resize(image, resize_dim)
    
    # Apply Gaussian Blur if requested
    if apply_blur:
        processed_img = cv2.GaussianBlur(processed_img, (5, 5), 0)
        
    return processed_img

def pil_to_cv2(pil_image):
    \"\"\"Convert PIL Image to OpenCV format (numpy array)\"\"\"
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv2_image):
    \"\"\"Convert OpenCV format to PIL Image\"\"\"
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
