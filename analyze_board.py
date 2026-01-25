import cv2
import numpy as np

# Load the image
img = cv2.imread(r"C:\Users\philo\.gemini\antigravity\brain\6fc9f17a-e3ce-4792-9bd1-0e3782130009\uploaded_image_1767559905752.png")

h, w, _ = img.shape
print(f"Image size: {w}x{h}")

# Calculate board position (same as vision.py)
aspect_ratio = h / w
if aspect_ratio < 1.5:
    max_board_h = int(h * 0.70)
    target_board_w = int(w * 0.92)
    BOARD_SIZE = min(target_board_w, max_board_h)
    BOARD_X = (w - BOARD_SIZE) // 2
    BOARD_Y = int(h * 0.05)
else:
    BOARD_SIZE = int(w * 0.92)
    BOARD_X = int(w * 0.04)
    BOARD_Y = int(h * 0.23)

CELL_SIZE = BOARD_SIZE // 8
print(f"Board: Y={BOARD_Y}, X={BOARD_X}, Size={BOARD_SIZE}, Cell={CELL_SIZE}")

# Extract board
board_img = img[BOARD_Y:BOARD_Y+BOARD_SIZE, BOARD_X:BOARD_X+BOARD_SIZE]

# Sample cells from row 2 (which has filled cells in the image)
print("\n--- Sampling cells from Row 2 ---")
padding = int(CELL_SIZE * 0.15)

for c in range(8):
    r = 2
    x1 = c * CELL_SIZE
    y1 = r * CELL_SIZE
    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE
    
    cell = board_img[y1+padding:y2-padding, x1+padding:x2-padding]
    
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    avg_gray = np.mean(gray)
    
    hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
    avg_sat = np.mean(hsv[:,:,1])
    avg_val = np.mean(hsv[:,:,2])
    
    # Current logic: Gray < 150 AND Sat > 150 = Filled
    is_filled_old = avg_gray < 150 and avg_sat > 150
    
    print(f"Cell (2,{c}): Gray={avg_gray:.1f}, Sat={avg_sat:.1f}, Val={avg_val:.1f} -> {'FILLED' if is_filled_old else 'EMPTY'}")

# Also check row 0 (which should be empty)
print("\n--- Sampling cells from Row 0 ---")
for c in range(8):
    r = 0
    x1 = c * CELL_SIZE
    y1 = r * CELL_SIZE
    
    cell = board_img[y1+padding:y1+CELL_SIZE-padding, x1+padding:x1+CELL_SIZE-padding]
    
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    avg_gray = np.mean(gray)
    
    hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
    avg_sat = np.mean(hsv[:,:,1])
    
    is_filled_old = avg_gray < 150 and avg_sat > 150
    
    print(f"Cell (0,{c}): Gray={avg_gray:.1f}, Sat={avg_sat:.1f} -> {'FILLED' if is_filled_old else 'EMPTY'}")
