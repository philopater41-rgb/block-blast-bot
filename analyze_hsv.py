import cv2
import numpy as np

def analyze_hsv(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Calculate average HSV
    avg_hsv = np.mean(hsv, axis=(0,1))
    print(f"Average HSV: {avg_hsv}")
    
    # Calculate HSV of center of image (likely background)
    h, w, _ = hsv.shape
    center_hsv = hsv[h//2, w//2]
    print(f"Center HSV: {center_hsv}")
    
    # Calculate HSV of a likely block area (e.g., left side)
    block_hsv = hsv[h//2, w//4] # Roughly center of left slot
    print(f"Left Slot Center HSV: {block_hsv}")

if __name__ == "__main__":
    analyze_hsv("debug_issue.png")
