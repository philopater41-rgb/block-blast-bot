import cv2
import numpy as np
import sys

def analyze_blue_theme(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image")
        return

    h, w, _ = img.shape
    print(f"Image size: {w}x{h}")
    
    # Crop shape area (bottom 30%)
    start_y = int(h * 0.70)
    shape_area = img[start_y:, :]
    
    cv2.imwrite("debug_blue_area.png", shape_area)
    
    hsv = cv2.cvtColor(shape_area, cv2.COLOR_BGR2HSV)
    
    # Sample points
    # Assuming standard positions for slots
    slot_width = w // 3
    y_center = shape_area.shape[0] // 2
    
    points = [
        (slot_width // 2, y_center, "Slot 1 Center"),
        (slot_width + slot_width // 2, y_center, "Slot 2 Center"),
        (2 * slot_width + slot_width // 2, y_center, "Slot 3 Center"),
        (10, 10, "Background Top-Left"),
        (w // 2, 10, "Background Top-Center")
    ]
    
    print("\nHSV Analysis:")
    for x, y, name in points:
        if 0 <= y < hsv.shape[0] and 0 <= x < hsv.shape[1]:
            pixel = hsv[y, x]
            print(f"{name} ({x},{y}): HSV={pixel}")
            
    # Check BGR channels
    b, g, r = cv2.split(shape_area)
    print(f"\nBGR Stats:")
    print(f"Blue: Mean={np.mean(b)}")
    print(f"Green: Mean={np.mean(g)}")
    print(f"Red: Mean={np.mean(r)}")
    
    # Sample points in BGR
    print("\nBGR Samples:")
    for x, y, name in points:
        if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
            pixel = shape_area[y, x] # Note: shape_area coordinates
            print(f"{name} ({x},{y}): BGR={pixel}")

    # Check Lab
    lab = cv2.cvtColor(shape_area, cv2.COLOR_BGR2Lab)
    l, a, b_lab = cv2.split(lab)
    print(f"\nLab Stats:")
    print(f"L (Lightness): Mean={np.mean(l)}")
    
    print("\nLab Samples:")
    for x, y, name in points:
        if 0 <= y < lab.shape[0] and 0 <= x < lab.shape[1]:
            pixel = lab[y, x]
            print(f"{name} ({x},{y}): Lab={pixel}")
            
    # Test Adaptive Thresholding on V channel (since it has high mean)
    print("\nTesting Adaptive Thresholding:")
    v_channel = hsv[:,:,2]
    thresh_adapt = cv2.adaptiveThreshold(v_channel, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    cv2.imwrite("debug_blue_thresh_adapt.png", thresh_adapt)
    contours_adapt, _ = cv2.findContours(thresh_adapt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Adaptive Threshold: {len(contours_adapt)} contours")

if __name__ == "__main__":
    analyze_blue_theme("debug_blue_theme.png")
