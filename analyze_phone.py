import cv2
import numpy as np
import subprocess

def capture_and_analyze():
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
    
    # Decode image
    nparr = np.frombuffer(screenshot_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        print("ERROR: Could not decode image")
        return
    
    h, w, _ = img.shape
    print(f"Phone Screen: {w}x{h}")
    
    # Calculate board position
    aspect_ratio = h / w
    print(f"Aspect Ratio: {aspect_ratio:.2f}")
    
    if aspect_ratio < 1.5:
        max_board_h = int(h * 0.70)
        target_board_w = int(w * 0.92)
        BOARD_SIZE = min(target_board_w, max_board_h)
        BOARD_X = (w - BOARD_SIZE) // 2
        BOARD_Y = int(h * 0.05)
    else:
        # Precise user measurements
        BOARD_X = 65
        BOARD_Y = 584
        BOARD_SIZE = 950
        
        if BOARD_Y + BOARD_SIZE > h:
            BOARD_Y = int(h * 0.15)
    
    CELL_SIZE = BOARD_SIZE // 8
    
    print(f"\n=== CALCULATED BOARD POSITION ===")
    print(f"BOARD_X = {BOARD_X}")
    print(f"BOARD_Y = {BOARD_Y}")
    print(f"BOARD_SIZE = {BOARD_SIZE}")
    print(f"CELL_SIZE = {CELL_SIZE}")
    print(f"Board ends at Y = {BOARD_Y + BOARD_SIZE}")
    
    # Draw the detected board area
    debug_img = img.copy()
    
    # Draw board rectangle (Green)
    cv2.rectangle(debug_img, 
                  (BOARD_X, BOARD_Y), 
                  (BOARD_X + BOARD_SIZE, BOARD_Y + BOARD_SIZE), 
                  (0, 255, 0), 5)
    
    # Draw grid lines (Blue)
    for i in range(9):
        # Vertical lines
        x = BOARD_X + i * CELL_SIZE
        cv2.line(debug_img, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), (255, 0, 0), 2)
        # Horizontal lines
        y = BOARD_Y + i * CELL_SIZE
        cv2.line(debug_img, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), (255, 0, 0), 2)
    
    # Save debug image
    cv2.imwrite("debug_board_position.png", debug_img)
    print("\nSaved: debug_board_position.png")
    
    # Also save the raw capture
    cv2.imwrite("debug_raw_capture.png", img)
    print("Saved: debug_raw_capture.png")
    
    # Sample theme
    start_y = int(h * 0.70)
    sample = img[start_y:start_y+10, 10:20]
    avg_color = np.mean(sample, axis=(0, 1))
    b, g, r = avg_color
    print(f"\n=== THEME DETECTION ===")
    print(f"Sample Color: B={b:.1f}, G={g:.1f}, R={r:.1f}")
    
    if b < 100 and g < 100 and r < 100:
        print("Theme: DARK")
    elif b > g + 20:
        print("Theme: BLUE")
    else:
        print("Theme: GREEN")

if __name__ == "__main__":
    capture_and_analyze()
