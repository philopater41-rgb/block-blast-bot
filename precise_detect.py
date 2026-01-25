import cv2
import numpy as np
import subprocess

def precise_board_detection():
    print("Capturing screen from phone...")
    
    process = subprocess.Popen(
        ['adb', 'exec-out', 'screencap', '-p'],
        stdout=subprocess.PIPE
    )
    screenshot_data, _ = process.communicate()
    
    if not screenshot_data:
        print("ERROR: No data received from ADB")
        return
    
    nparr = np.frombuffer(screenshot_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        print("ERROR: Could not decode image")
        return
    
    h, w, _ = img.shape
    print(f"Phone Screen: {w}x{h}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # The board border is a lighter gray line around a darker gray board
    # Let's find the exact edges by looking for color transitions
    
    # Sample row at approximately the board center (y = 0.4 * h)
    center_y = int(h * 0.35)
    
    # Find left inner edge - look for transition from border to cell area
    left_x = 0
    for x in range(50, w//2):
        # Look for the inner edge (darker to darker transition after border)
        if gray[center_y, x] < 100:  # Inside the dark board
            # Go back a few pixels to find where the border starts
            for bx in range(x, 0, -1):
                if gray[center_y, bx] > 80:  # Border is slightly lighter
                    left_x = bx + 5  # Skip the border
                    break
            break
    
    # Find right inner edge
    right_x = w
    for x in range(w-50, w//2, -1):
        if gray[center_y, x] < 100:  # Inside dark board
            for bx in range(x, w):
                if gray[center_y, bx] > 80:
                    right_x = bx - 5
                    break
            break
    
    # Find top inner edge
    center_x = w // 2
    top_y = 0
    for y in range(100, h//2):
        if gray[y, center_x] < 100:  # Inside dark board
            for by in range(y, 0, -1):
                if gray[by, center_x] > 80:
                    top_y = by + 5
                    break
            break
    
    # Find bottom inner edge
    bottom_y = h
    for y in range(h * 2 // 3, h // 3, -1):
        if gray[y, center_x] < 100:
            for by in range(y, h):
                if gray[by, center_x] > 80:
                    bottom_y = by - 5
                    break
            break
    
    print(f"\n=== PRECISE BOARD DETECTION ===")
    print(f"Inner Left: {left_x}")
    print(f"Inner Right: {right_x}")
    print(f"Inner Top: {top_y}")
    print(f"Inner Bottom: {bottom_y}")
    
    inner_width = right_x - left_x
    inner_height = bottom_y - top_y
    print(f"Inner Width: {inner_width}")
    print(f"Inner Height: {inner_height}")
    
    # Use the smaller dimension for square board
    BOARD_SIZE = min(inner_width, inner_height)
    BOARD_X = left_x
    BOARD_Y = top_y
    CELL_SIZE = BOARD_SIZE // 8
    
    print(f"\n=== FINAL VALUES ===")
    print(f"BOARD_X = {BOARD_X} ({BOARD_X/w:.4f} * w)")
    print(f"BOARD_Y = {BOARD_Y} ({BOARD_Y/h:.4f} * h)")
    print(f"BOARD_SIZE = {BOARD_SIZE} ({BOARD_SIZE/w:.4f} * w)")
    print(f"CELL_SIZE = {CELL_SIZE}")
    
    # Draw on image
    debug_img = img.copy()
    cv2.rectangle(debug_img, (BOARD_X, BOARD_Y), (BOARD_X + BOARD_SIZE, BOARD_Y + BOARD_SIZE), (0, 255, 0), 3)
    
    for i in range(9):
        x = BOARD_X + i * CELL_SIZE
        cv2.line(debug_img, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), (255, 0, 0), 2)
        y = BOARD_Y + i * CELL_SIZE
        cv2.line(debug_img, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), (255, 0, 0), 2)
    
    cv2.imwrite("debug_precise_board.png", debug_img)
    print("\nSaved: debug_precise_board.png")

if __name__ == "__main__":
    precise_board_detection()
