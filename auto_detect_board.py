import cv2
import numpy as np
import subprocess

def auto_detect_board():
    print("Capturing screen from phone...")
    
    # Capture using ADB
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
    
    # Convert to grayscale and find edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Look for the board by finding the dark gray rectangle
    # The board background is dark gray (~63), surrounded by slightly different gray
    
    # Scan horizontally at y=h*0.5 to find board edges
    mid_y = int(h * 0.4)  # Middle of expected board area
    row = gray[mid_y, :]
    
    # Find left edge (transition from background to board)
    left_edge = 0
    for x in range(w // 4):  # Only check left quarter
        if abs(int(row[x]) - int(row[x+5])) > 10:  # Transition
            left_edge = x
            break
    
    # Find right edge
    right_edge = w
    for x in range(w-1, w * 3 // 4, -1):  # Only check right quarter
        if abs(int(row[x]) - int(row[x-5])) > 10:  # Transition
            right_edge = x
            break
    
    # Scan vertically at x=w//2 to find top/bottom edges
    mid_x = w // 2
    col = gray[:, mid_x]
    
    # Find top edge
    top_edge = 0
    for y in range(h // 4):
        if abs(int(col[y]) - int(col[y+5])) > 10:
            top_edge = y
            break
    
    # Find bottom edge of board
    bottom_edge = h
    for y in range(h * 3 // 4, h // 4, -1):
        if abs(int(col[y]) - int(col[y-5])) > 10:
            bottom_edge = y
            break
    
    print(f"\n=== AUTO-DETECTED BOARD EDGES ===")
    print(f"Left: {left_edge}, Right: {right_edge}")
    print(f"Top: {top_edge}, Bottom: {bottom_edge}")
    
    detected_width = right_edge - left_edge
    detected_height = bottom_edge - top_edge
    print(f"Detected Size: {detected_width}x{detected_height}")
    
    # Use the smaller of width/height for a square board
    BOARD_SIZE = min(detected_width, detected_height)
    BOARD_X = left_edge
    BOARD_Y = top_edge
    CELL_SIZE = BOARD_SIZE // 8
    
    print(f"\n=== SUGGESTED VALUES ===")
    print(f"BOARD_X = {BOARD_X} ({BOARD_X/w:.4f} * w)")
    print(f"BOARD_Y = {BOARD_Y} ({BOARD_Y/h:.4f} * h)")
    print(f"BOARD_SIZE = {BOARD_SIZE} ({BOARD_SIZE/w:.4f} * w)")
    print(f"CELL_SIZE = {CELL_SIZE}")
    
    # Draw debug image
    debug_img = img.copy()
    cv2.rectangle(debug_img, (BOARD_X, BOARD_Y), (BOARD_X + BOARD_SIZE, BOARD_Y + BOARD_SIZE), (0, 255, 0), 5)
    
    for i in range(9):
        x = BOARD_X + i * CELL_SIZE
        cv2.line(debug_img, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), (255, 0, 0), 2)
        y = BOARD_Y + i * CELL_SIZE
        cv2.line(debug_img, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), (255, 0, 0), 2)
    
    cv2.imwrite("debug_auto_detect.png", debug_img)
    print("\nSaved: debug_auto_detect.png")

if __name__ == "__main__":
    auto_detect_board()
