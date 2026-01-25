import cv2
import numpy as np

import sys

def parse_shapes_debug(image):
    h, w, _ = image.shape
    print(f"Image size: {w}x{h}")
    sys.stdout.flush()
    
    # Crop bottom 30%
    start_y = int(h * 0.65)
    shape_area = image[start_y:, :]
    
    print(f"Shape area size: {shape_area.shape}")
    cv2.imwrite("debug_repro_area.png", shape_area)
    
    # Convert to HSV
    hsv = cv2.cvtColor(shape_area, cv2.COLOR_BGR2HSV)
    
    # Sample Saturation profile across the middle
    print("Saturation Profile (y=115):")
    s_values = []
    for x in range(0, w, 10):
        s = hsv[115, x][1]
        s_values.append(str(s))
    print(",".join(s_values))
    sys.stdout.flush()
    
    # Filter by Saturation
    lower_green = np.array([35, 20, 20]) 
    upper_green = np.array([90, 80, 180])
    
    thresh = cv2.inRange(hsv, lower_green, upper_green)
    cv2.imwrite("debug_repro_thresh_raw.png", thresh)
    
    print("Done thresholding")
    sys.stdout.flush()
    
    # Morphological operations
    # Use OPEN to remove small background noise (texture)
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    cv2.imwrite("debug_repro_thresh_morph.png", thresh)
    
    print("Starting findContours")
    sys.stdout.flush()
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} total contours")
    
    valid_contours = []
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        
        cx, cy = x + w//2, y + h//2
        if 0 <= cy < hsv.shape[0] and 0 <= cx < hsv.shape[1]:
            pixel_hsv = hsv[cy, cx]
            print(f"Contour {i}: Area={area}, BBox=({x},{y},{w},{h}), CenterHSV={pixel_hsv}")
        else:
            print(f"Contour {i}: Area={area}, BBox=({x},{y},{w},{h})")
        
        if area > 50: 
            valid_contours.append(cnt)
            
    print(f"Valid contours: {len(valid_contours)}")
    
    debug_img = shape_area.copy()
    cv2.drawContours(debug_img, valid_contours, -1, (0, 0, 255), 2)
    cv2.imwrite("debug_repro_contours.png", debug_img)

if __name__ == "__main__":
    img = cv2.imread("debug_failure_case.png")
    if img is None:
        print("Could not read image")
    else:
        parse_shapes_debug(img)
