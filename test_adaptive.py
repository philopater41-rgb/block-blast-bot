import cv2
import numpy as np

def test_adaptive(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image")
        return

    # Upscale image to match standard resolution (width 1080)
    target_width = 1080
    scale = target_width / img.shape[1]
    target_height = int(img.shape[0] * scale)
    img = cv2.resize(img, (target_width, target_height))
    
    h, w, _ = img.shape
    # Crop shape area (bottom 30%)
    start_y = int(h * 0.70)
    if start_y < 1600 and h > 2000: start_y = 1600 # Sync with vision.py logic
    
    shape_area = img[start_y:, :]
    
    # Convert to Grayscale
    gray = cv2.cvtColor(shape_area, cv2.COLOR_BGR2GRAY)
    
    # Adaptive Thresholding
    # ADAPTIVE_THRESH_GAUSSIAN_C: weighted sum of neighbourhood values
    # Block Size: 11 (must be odd)
    # C: 2 (constant subtracted from mean)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3)
    cv2.imwrite("debug_adaptive_raw.png", thresh)
    
    # Morphological operations to clean up and fill
    # 1. Open to remove small noise (texture)
    kernel_open = np.ones((3,3), np.uint8)
    thresh_open = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open)
    cv2.imwrite("debug_adaptive_open.png", thresh_open)
    
    # 2. Close/Dilate to connect edges and fill blocks
    kernel_close = np.ones((7,7), np.uint8)
    thresh_close = cv2.morphologyEx(thresh_open, cv2.MORPH_CLOSE, kernel_close)
    cv2.imwrite("debug_adaptive_close.png", thresh_close)
    
    # Find contours
    contours, _ = cv2.findContours(thresh_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} contours")
    
    # Filter and Draw
    valid_contours = []
    debug_img = shape_area.copy()
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Filter small noise
        if area > 200:
            valid_contours.append(cnt)
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
    print(f"Valid contours (>200 area): {len(valid_contours)}")
    cv2.imwrite("debug_adaptive_result.png", debug_img)

if __name__ == "__main__":
    test_adaptive("debug_blue_theme.png")
