import cv2
import numpy as np
import vision

def analyze_board_cells(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image")
        return

    # Upscale image to match standard resolution (width 1080)
    target_width = 1080
    scale = target_width / img.shape[1]
    target_height = int(img.shape[0] * scale)
    img = cv2.resize(img, (target_width, target_height))
    print(f"Upscaled Image to: {img.shape}")

    # Constants from vision.py
    BOARD_X = 45
    BOARD_Y = 564 # This might need adjustment if aspect ratio is different
    BOARD_SIZE = 990
    GRID_SIZE = 8
    CELL_SIZE = BOARD_SIZE // GRID_SIZE
    
    # Check if BOARD_Y fits
    if BOARD_Y + BOARD_SIZE > img.shape[0]:
        print("WARNING: Board area exceeds image height. Adjusting Y...")
        # Try to center it? Or just assume it's higher up.
        # For 305x685 -> 1080x2425. 
        # 564 + 990 = 1554. Fits easily.
    
    board_img = img[BOARD_Y:BOARD_Y+BOARD_SIZE, BOARD_X:BOARD_X+BOARD_SIZE]
    cv2.imwrite("debug_board_crop.png", board_img)
    
    print("--- Board Cell Analysis ---")
    
    # Sample cells from uploaded_image_1767549320554.png
    # Row 0, Col 7 is FILLED (Top Right)
    # Row 0, Col 0 is EMPTY (Top Left)
    # Row 1, Col 7 is FILLED
    
    cells_to_check = [
        (0, 0, "Empty (Top-Left)"),
        (0, 7, "Filled (Top-Right)"),
        (1, 7, "Filled (Row 1, Col 7)")
    ]
    
    for r, c, label in cells_to_check:
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        
        # Dynamic padding
        padding = int(CELL_SIZE * 0.15)
        cell = board_img[y1+padding:y2-padding, x1+padding:x2-padding]
        
        if cell.size == 0:
            print(f"Cell ({r}, {c}) is empty/out of bounds!")
            continue
            
        avg_bgr = np.mean(cell, axis=(0, 1))
        gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        avg_gray = np.mean(gray)
        
        hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
        avg_hsv = np.mean(hsv, axis=(0, 1))
        
        print(f"\nCell ({r}, {c}) - {label}:")
        print(f"  Avg BGR: {avg_bgr}")
        print(f"  Avg Gray: {avg_gray:.2f}")
    # Sample T-shape area (Bottom Right)
    # Image size 488x454.
    # T-shape is likely around x=350-450, y=380-440.
    
    # Let's sample a point in the T-shape
    # Visual inspection: Bottom right corner.
    
    # Create a dummy "cell" for the shape
    shape_x = 400
    shape_y = 400
    shape_size = 30
    
    shape_cell = img[shape_y:shape_y+shape_size, shape_x:shape_x+shape_size]
    
    if shape_cell.size > 0:
        avg_bgr = np.mean(shape_cell, axis=(0, 1))
        hsv = cv2.cvtColor(shape_cell, cv2.COLOR_BGR2HSV)
        avg_hsv = np.mean(hsv, axis=(0, 1))
        
        print(f"\nShape Sample (approx):")
        print(f"  Avg BGR: {avg_bgr}")
        print(f"  Avg HSV: {avg_hsv}")
        cv2.imwrite("debug_shape_sample.png", shape_cell)
    else:
        print("Shape sample out of bounds")

if __name__ == "__main__":
    # Use the absolute path to the uploaded image
    analyze_board_cells(r"C:/Users/philo/.gemini/antigravity/brain/6fc9f17a-e3ce-4792-9bd1-0e3782130009/uploaded_image_1767549320554.png")
