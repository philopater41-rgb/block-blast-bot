import cv2
import numpy as np

def analyze_shapes(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image")
        return

    print(f"Shape area size: {img.shape}")
    
    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Green color range in HSV
    # Background is Saturated (S~93), Blocks are less saturated (S~50)
    # Filter by LOW Saturation
    lower_green = np.array([35, 20, 20]) 
    upper_green = np.array([90, 80, 180]) # S max 80, V max 180
    
    thresh = cv2.inRange(hsv, lower_green, upper_green)
    print(f"Mask non-zero pixels: {cv2.countNonZero(thresh)}")
    
    # Morphological operations
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    cv2.imwrite("debug_shapes_thresh.png", thresh)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter small noise AND large background noise
    # Blocks are roughly 50x50 (area ~2500). 
    # Max shape size is 3x3 (area ~22500).
    # Filter anything < 500 or > 30000 (to avoid full width lines)
    valid_contours = [cnt for cnt in contours if 500 < cv2.contourArea(cnt) < 30000]
    
    # Sort by x coordinate
    valid_contours.sort(key=lambda c: cv2.boundingRect(c)[0])
    
    # Dynamic slots
    # The crop might be slightly off, so let's use fixed relative positions
    # or cluster them.
    # Simple clustering by X coordinate.
    
    slots = [[], [], []]
    if not valid_contours:
        return
        
    # Cluster centers
    centers = [cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2]//2 for c in valid_contours]
    
    # We expect 3 clusters. Use K-Means or simple thresholding.
    # Since they are sorted, we can just look for gaps.
    
    current_slot = 0
    slots[0].append(valid_contours[0])
    last_center = centers[0]
    
    for i in range(1, len(valid_contours)):
        center = centers[i]
        # If gap is large enough (> 100px), move to next slot
        if center - last_center > 100:
            current_slot += 1
            if current_slot > 2: break # Should not happen if only 3 shapes
            
        slots[current_slot].append(valid_contours[i])
        last_center = center
            
    for i, slot_contours in enumerate(slots):
        print(f"Slot {i+1}: {len(slot_contours)} contours")
        if slot_contours:
            # Draw bounding box for the whole slot
            all_points = np.concatenate(slot_contours)
            x, y, w, h = cv2.boundingRect(all_points)
            area = cv2.contourArea(all_points) 
            print(f"  BBox: x={x}, y={y}, w={w}, h={h}")
            print(f"  Aspect Ratio: {w/h:.2f}")
            print(f"  Area: {area}")
            
            # Analyze individual contours in the slot
            for cnt in slot_contours:
                cx, cy, cw, ch = cv2.boundingRect(cnt)
                print(f"    Block: x={cx}, y={cy}, w={cw}, h={ch}")
            
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
    cv2.imwrite("debug_shapes_analyzed.png", img)

if __name__ == "__main__":
    analyze_shapes("debug_issue_2.png")
