import cv2
import numpy as np
import subprocess

# Module-level globals for board coordinates (updated by parse_board)
BOARD_X = 0
BOARD_Y = 0
BOARD_SIZE = 0
CELL_SIZE = 0

def capture_screen():
    """Captures the screen from the connected Android device."""
    try:
        # Capture screen using ADB
        process = subprocess.Popen(
            ['adb', 'exec-out', 'screencap', '-p'],
            stdout=subprocess.PIPE
        )
        screenshot_data, _ = process.communicate()
        
        if not screenshot_data:
            print("Error: No data received from ADB.")
            return None

        # Convert to numpy array
        image_array = np.frombuffer(screenshot_data, np.uint8)
        
        # Decode image
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        return image
    except Exception as e:
        print(f"Error capturing screen: {e}")
        return None

# Global constants for UI drawing (updated dynamically)
BOARD_X = 45
BOARD_Y = 564
BOARD_SIZE = 990
GRID_SIZE = 8
CELL_SIZE = BOARD_SIZE // GRID_SIZE

def parse_board(image):
    """
    Parses the 8x8 grid from the screenshot.
    Returns a numpy matrix (8x8) where 1=filled, 0=empty.
    """
    global BOARD_X, BOARD_Y, BOARD_SIZE, CELL_SIZE
    
    h, w, _ = image.shape
    
    # Smart Board Positioning
    # Check aspect ratio
    aspect_ratio = h / w
    
    if aspect_ratio < 1.5:
        # Short/Square image (Cropped window)
        # We MUST reserve space for shapes at the bottom (approx 25-30%)
        max_board_h = int(h * 0.70)
        target_board_w = int(w * 0.92)
        
        BOARD_SIZE = min(target_board_w, max_board_h)
        
        # Center the board horizontally
        BOARD_X = (w - BOARD_SIZE) // 2
        
        # Position board at top with small margin
        BOARD_Y = int(h * 0.05)
            
    else:
        # Tall image (Phone screen) - precise user measurements
        # Top-Left: (65, 584), Bottom-Right: (1015, 1533)
        # Width: 1015 - 65 = 950
        # Height: 1533 - 584 = 949
        BOARD_X = 65
        BOARD_Y = 584
        BOARD_SIZE = 950
        
        if BOARD_Y + BOARD_SIZE > h:
            BOARD_Y = int(h * 0.15)
    
    CELL_SIZE = BOARD_SIZE // GRID_SIZE
    
    # Detect theme first
    theme = detect_theme(image)
    print(f"Parsing Board with Theme: {theme}")
    
    board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    
    # Extract board area
    board_img = image[BOARD_Y:BOARD_Y+BOARD_SIZE, BOARD_X:BOARD_X+BOARD_SIZE]
    
    if board_img.size == 0:
        print("ERROR: Board image is empty! Check coordinates.")
        return board
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            
            # Sample center of cell to avoid borders
            # Dynamic padding: 15% of cell size
            padding = int(CELL_SIZE * 0.15)
            cell = board_img[y1+padding:y2-padding, x1+padding:x2-padding]
            
            if theme == 'BLUE':
                # Blue Theme: Filled cells are DARKER and MORE SATURATED
                # Empty: Gray ~197, Sat ~100
                # Filled: Gray ~78, Sat ~227
                
                gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
                avg_gray = np.mean(gray)
                
                # Check Saturation as secondary confirmation
                hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
                avg_sat = np.mean(hsv[:,:,1])
                
                # Logic: Darker (< 150) AND Saturated (> 150)
                if avg_gray < 150 and avg_sat > 150:
                    board[r, c] = 1
                else:
                    board[r, c] = 0
                    
            elif theme == 'DARK':
                # Dark Theme: Filled cells are BRIGHTER and COLORFUL
                # Empty: Gray ~63 (dark gray)
                # Filled: Bright colored (green, red, etc.) - Sat > 100, Val > 100
                
                hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
                avg_sat = np.mean(hsv[:,:,1])
                avg_val = np.mean(hsv[:,:,2])
                
                # Logic: Saturated (> 100) AND Bright (> 80)
                if avg_sat > 100 and avg_val > 80:
                    board[r, c] = 1
                else:
                    board[r, c] = 0
                    
            else:
                # Green/Original Theme: Filled cells are BRIGHTER
                avg_color = np.mean(cell)
                if avg_color > 100:
                    board[r, c] = 1
                else:
                    board[r, c] = 0
                    
    return board

def get_shape_area(image):
    """
    Extracts the area where shapes are located.
    """
    h, w, _ = image.shape
    
    # Replicate smart positioning logic
    aspect_ratio = h / w
    if aspect_ratio < 1.5:
        max_board_h = int(h * 0.70)
        target_board_w = int(w * 0.92)
        BOARD_SIZE = min(target_board_w, max_board_h)
        BOARD_Y = int(h * 0.05)
    else:
        BOARD_SIZE = int(w * 0.92)
        BOARD_Y = int(h * 0.23)
        if BOARD_Y + BOARD_SIZE > h: BOARD_Y = int(h * 0.15)
    
    # Shapes are below the board
    start_y = BOARD_Y + BOARD_SIZE + int(h * 0.02) # Small padding
    return image[start_y:, :]

def detect_theme(image):
    """
    Detects the color theme of the game.
    Returns 'DARK', 'BLUE', or 'GREEN'.
    """
    # Sample background color (top-left of shape area)
    h, w, _ = image.shape
    start_y = int(h * 0.70)
    
    # Sample a 10x10 area
    sample = image[start_y:start_y+10, 10:20]
    avg_color = np.mean(sample, axis=(0, 1)) # BGR
    b, g, r = avg_color
    
    print(f"Theme Detection - Avg Color: B={b:.1f}, G={g:.1f}, R={r:.1f}")
    
    # Dark theme: All values are low (< 100)
    if b < 100 and g < 100 and r < 100:
        return 'DARK'
    # Blue theme: B > G + 20
    elif b > g + 20:
        return 'BLUE'
    else:
        return 'GREEN'

def parse_shapes_adaptive(image):
    """
    Parses shapes using HSV Value thresholding (for Blue Theme).
    Shapes are DARKER than background.
    """
    h, w, _ = image.shape
    
    # Constants - Calculate SPAWN_Y1 based on board position
    aspect_ratio = h / w
    
    # Calculate board end position first
    if aspect_ratio < 1.5:
        # Cropped window
        max_board_h = int(h * 0.70)
        target_board_w = int(w * 0.92)
        board_sz = min(target_board_w, max_board_h)
        board_y = int(h * 0.05)
        SPAWN_Y1 = board_y + board_sz + int(h * 0.02)  # Board end + small gap
    else:
        # Phone screen - calculate board end and add gap
        board_sz = int(w * 0.92)
        board_y = int(h * 0.23)
        if board_y + board_sz > h:
            board_y = int(h * 0.15)
        SPAWN_Y1 = board_y + board_sz + int(h * 0.02)  # Board end + small gap 
    
    SPAWN_Y2 = h
    
    # Dynamic Block Size
    if aspect_ratio < 1.5:
        max_board_h = int(h * 0.70)
        target_board_w = int(w * 0.92)
        board_sz = min(target_board_w, max_board_h)
        cell_sz = board_sz // 8
        BLOCK_SIZE_REF = max(10, int(cell_sz * 0.85))
    else:
        # Phone screen: Smaller blocks = more accurate detection
        board_sz = int(w * 0.92)
        cell_sz = board_sz // 8
        BLOCK_SIZE_REF = max(10, int(cell_sz * 0.50))
    
    # Extract shape area
    shape_area = image[SPAWN_Y1:SPAWN_Y2, :]
    print(f"DEBUG Shape: SPAWN_Y1={SPAWN_Y1}, SPAWN_Y2={SPAWN_Y2}, shape_area size={shape_area.shape}")
    
    # Convert to HSV
    hsv = cv2.cvtColor(shape_area, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:,:,2]
    s_channel = hsv[:,:,1]
    
    # For Blue Theme: Shapes are DARKER and MORE SATURATED than background
    # Background: Light blue (V > 240, S ~150)
    # Shapes: Dark blue (V < 230) OR High saturated (S > 180)
    
    # Detect DARK shapes (low Value) - V threshold raised to 230
    _, mask_dark = cv2.threshold(v_channel, 230, 255, cv2.THRESH_BINARY_INV)
    
    # Detect HIGH SATURATION shapes (S > 180) but NOT bright background
    _, mask_sat = cv2.threshold(s_channel, 180, 255, cv2.THRESH_BINARY)
    _, mask_not_bright = cv2.threshold(v_channel, 240, 255, cv2.THRESH_BINARY_INV)
    mask_saturated = cv2.bitwise_and(mask_sat, mask_not_bright)
    
    # Combined mask
    thresh_original = cv2.bitwise_or(mask_dark, mask_saturated)
    
    # DEBUG: Save masks
    cv2.imwrite("debug_shape_area.png", shape_area)
    cv2.imwrite("debug_mask_dark.png", mask_dark)
    cv2.imwrite("debug_mask_sat.png", mask_saturated)
    cv2.imwrite("debug_thresh.png", thresh_original)
    
    # Morphological operations - use dilated version ONLY for contour detection
    kernel = np.ones((5,5), np.uint8)
    thresh_dilated = cv2.dilate(thresh_original, kernel, iterations=2)
    
    # Find contours on dilated mask
    contours, _ = cv2.findContours(thresh_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"DEBUG: Found {len(contours)} contours before filtering")
    
    # Use ORIGINAL thresh for pixel checking (not dilated)
    thresh = thresh_original
    
    slot_width = w // 3
    parsed_shapes = []
    slots = [[], [], []]
    
    # Lower min_area to detect smaller shapes
    min_area = (BLOCK_SIZE_REF * BLOCK_SIZE_REF) * 0.15
    
    if contours:
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, cw, ch = cv2.boundingRect(cnt)
            print(f"DEBUG Contour: area={area:.1f}, min_area={min_area:.1f}, x={x}, y={y}, w={cw}, h={ch}")
            
            if area < min_area:
                print("  -> FILTERED: area too small")
                continue
            
            # Filter edge noise: Skip thin vertical contours (width < 15)
            if cw < 15:
                print("  -> FILTERED: width too small")
                continue
            
            # Filter bottom noise: Skip contours in bottom 40% of shape area (watermarks/UI)
            shape_area_height = shape_area.shape[0]
            if y > shape_area_height * 0.6:
                print(f"  -> FILTERED: bottom noise (y={y} > {shape_area_height * 0.6:.0f})")
                continue
            
            center_x = x + cw // 2
            
            # Simple slot assignment (no padding)
            slot_idx = min(2, center_x // slot_width)
            print(f"  -> ASSIGNED to slot {slot_idx}")
            if 0 <= slot_idx < 3:
                slots[slot_idx].append(cnt)
                
    # DEBUG: Visualize Contours
    debug_viz = shape_area.copy()
    cv2.drawContours(debug_viz, contours, -1, (0, 255, 0), 1)
    cv2.line(debug_viz, (slot_width, 0), (slot_width, shape_area.shape[0]), (0, 0, 255), 2)
    cv2.line(debug_viz, (slot_width*2, 0), (slot_width*2, shape_area.shape[0]), (0, 0, 255), 2)
    cv2.imwrite("debug_contours.png", debug_viz)
    
    # Process each slot
    for i in range(3):
        slot_contours = slots[i]
        if not slot_contours:
            parsed_shapes.append(([], None))
            continue
        
        print(f"DEBUG: Processing slot {i} with {len(slot_contours)} contours")
            
        all_points = np.concatenate(slot_contours)
        x, y, w_rect, h_rect = cv2.boundingRect(all_points)
        
        # Accordion Logic
        cols_count = max(1, int(round(w_rect / BLOCK_SIZE_REF)))
        rows_count = max(1, int(round(h_rect / BLOCK_SIZE_REF)))
        
        print(f"DEBUG: bbox x={x}, y={y}, w={w_rect}, h={h_rect}, cols={cols_count}, rows={rows_count}, BLOCK_SIZE_REF={BLOCK_SIZE_REF}")
        
        actual_cell_w = w_rect / cols_count
        actual_cell_h = h_rect / rows_count
        
        screen_bbox = (x, SPAWN_Y1 + y, w_rect, h_rect)
        shape_matrix = []
        
        for r in range(rows_count):
            for c_idx in range(cols_count):
                cx_rel = (c_idx * actual_cell_w) + (actual_cell_w / 2)
                cy_rel = (r * actual_cell_h) + (actual_cell_h / 2)
                
                mask_x = int(x + cx_rel)
                mask_y = int(y + cy_rel)
                
                # Sample 5x5 area around center
                y_min = max(0, mask_y - 2)
                y_max = min(thresh.shape[0], mask_y + 3)
                x_min = max(0, mask_x - 2)
                x_max = min(thresh.shape[1], mask_x + 3)
                
                roi = thresh[y_min:y_max, x_min:x_max]
                pixel_count = np.count_nonzero(roi)
                # Check if any pixels are present
                if pixel_count > 3:
                    shape_matrix.append((r, c_idx))
                    
        print(f"DEBUG: shape_matrix = {shape_matrix}")
        
        if not shape_matrix:
            parsed_shapes.append(([], None))
        else:
            parsed_shapes.append((shape_matrix, screen_bbox))
            
    return parsed_shapes

def parse_shapes(image):
    """
    Analyzes the bottom area for available shapes.
    Dispatches to the correct logic based on theme.
    """
    theme = detect_theme(image)
    print(f"Detected Theme: {theme}")
    
    if theme == 'BLUE':
        return parse_shapes_adaptive(image)
    elif theme == 'DARK':
        return parse_shapes_dark(image)
    else:
        # Use V12 Logic for Green/Original Theme
        return parse_shapes_v12(image)

def parse_shapes_dark(image):
    """
    Parses shapes for DARK theme.
    Shapes are BRIGHT and COLORFUL on dark background.
    """
    h, w, _ = image.shape
    
    # Constants - Calculate SPAWN_Y1 based on board position
    aspect_ratio = h / w
    
    if aspect_ratio < 1.5:
        max_board_h = int(h * 0.70)
        target_board_w = int(w * 0.92)
        board_sz = min(target_board_w, max_board_h)
        board_y = int(h * 0.05)
        SPAWN_Y1 = board_y + board_sz + int(h * 0.02)
    else:
        board_sz = int(w * 0.92)
        board_y = int(h * 0.23)
        if board_y + board_sz > h:
            board_y = int(h * 0.15)
        SPAWN_Y1 = board_y + board_sz + int(h * 0.02)
    
    SPAWN_Y2 = h
    
    # Dynamic Block Size - smaller = more blocks detected
    if aspect_ratio < 1.5:
        board_sz = min(int(w * 0.92), int(h * 0.70))
        cell_sz = board_sz // 8
        BLOCK_SIZE_REF = max(10, int(cell_sz * 0.65))  # Reduced from 0.85
    else:
        board_sz = int(w * 0.92)
        cell_sz = board_sz // 8
        BLOCK_SIZE_REF = max(10, int(cell_sz * 0.45))  # Increased from 0.40 to fix 5->6 issue
    
    # Extract shape area
    shape_area = image[SPAWN_Y1:SPAWN_Y2, :]
    print(f"DEBUG DARK Shape: SPAWN_Y1={SPAWN_Y1}, shape_area size={shape_area.shape}")
    
    # Convert to HSV - detect BRIGHT SATURATED shapes
    hsv = cv2.cvtColor(shape_area, cv2.COLOR_BGR2HSV)
    s_channel = hsv[:,:,1]
    v_channel = hsv[:,:,2]
    
    # Shapes are SATURATED (> 100) AND BRIGHT (> 80)
    _, mask_sat = cv2.threshold(s_channel, 100, 255, cv2.THRESH_BINARY)
    _, mask_val = cv2.threshold(v_channel, 80, 255, cv2.THRESH_BINARY)
    thresh = cv2.bitwise_and(mask_sat, mask_val)
    
    # Dilate to merge nearby pixels
    kernel = np.ones((5,5), np.uint8)
    thresh_dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(thresh_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"DEBUG DARK: Found {len(contours)} contours")
    
    slot_width = w // 3
    parsed_shapes = []
    slots = [[], [], []]
    
    min_area = (BLOCK_SIZE_REF * BLOCK_SIZE_REF) * 0.15
    shape_area_height = shape_area.shape[0]
    
    if contours:
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, cw, ch = cv2.boundingRect(cnt)
            
            if area < min_area: continue
            if cw < 15: continue
            if y > shape_area_height * 0.6: continue  # Filter bottom noise
            
            center_x = x + cw // 2
            slot_idx = min(2, center_x // slot_width)
            if 0 <= slot_idx < 3:
                slots[slot_idx].append(cnt)
    
    # Process each slot
    for i in range(3):
        slot_contours = slots[i]
        if not slot_contours:
            parsed_shapes.append(([], None))
            continue
            
        all_points = np.concatenate(slot_contours)
        x, y, w_rect, h_rect = cv2.boundingRect(all_points)
        
        cols_count = max(1, int(round(w_rect / BLOCK_SIZE_REF)))
        rows_count = max(1, int(round(h_rect / BLOCK_SIZE_REF)))
        
        actual_cell_w = w_rect / cols_count
        actual_cell_h = h_rect / rows_count
        
        screen_bbox = (x, SPAWN_Y1 + y, w_rect, h_rect)
        shape_matrix = []
        
        for r in range(rows_count):
            for c_idx in range(cols_count):
                cx_rel = (c_idx * actual_cell_w) + (actual_cell_w / 2)
                cy_rel = (r * actual_cell_h) + (actual_cell_h / 2)
                
                mask_x = int(x + cx_rel)
                mask_y = int(y + cy_rel)
                
                y_min = max(0, mask_y - 2)
                y_max = min(thresh.shape[0], mask_y + 3)
                x_min = max(0, mask_x - 2)
                x_max = min(thresh.shape[1], mask_x + 3)
                
                roi = thresh[y_min:y_max, x_min:x_max]
                if np.count_nonzero(roi) > 3:
                    shape_matrix.append((r, c_idx))
                    
        if not shape_matrix:
            parsed_shapes.append(([], None))
        else:
            parsed_shapes.append((shape_matrix, screen_bbox))
    
    # Save debug image
    debug_viz = shape_area.copy()
    cv2.drawContours(debug_viz, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("debug_dark_contours.png", debug_viz)
    
    return parsed_shapes

def parse_shapes_v12(image):
    """
    V12 Dilation & Accordion logic (Original for Green Theme).
    """
    h, w, _ = image.shape
    
    # Dynamic Constants
    aspect_ratio = h / w
    if aspect_ratio < 1.5:
        SPAWN_Y1 = int(h * 0.76) # Start below the board (which ends at ~0.75h)
    else:
        SPAWN_Y1 = int(h * 0.70) 
        if SPAWN_Y1 < 1600 and h > 2000: SPAWN_Y1 = 1600 
        
    SPAWN_Y2 = h
    
    # Dynamic Block Size (approx 4.7% of screen width)
    BLOCK_SIZE_REF = max(10, int(w * 0.047))
    
    TUNED_THRESHOLD = 120
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:,:,2]
    
    slot_width = w // 3
    parsed_shapes = []
    kernel = np.ones((7, 7), np.uint8)
    
    for i in range(3):
        x_start = i * slot_width
        x_end = (i + 1) * slot_width
        roi = v_channel[SPAWN_Y1:min(SPAWN_Y2, h), x_start:x_end]
        
        if roi.size == 0:
            parsed_shapes.append(([], None))
            continue
            
        _, mask = cv2.threshold(roi, TUNED_THRESHOLD, 255, cv2.THRESH_BINARY)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shape_matrix = []
        screen_bbox = None
        
        if contours:
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            valid_contour = None
            for c in sorted_contours:
                cx, cy, cw, ch = cv2.boundingRect(c)
                if cy < 10: continue
                if cv2.contourArea(c) > (BLOCK_SIZE_REF * BLOCK_SIZE_REF / 4):
                    valid_contour = c
                    break
            
            if valid_contour is not None:
                x, y, w_rect, h_rect = cv2.boundingRect(valid_contour)
                cols_count = max(1, int(round(w_rect / BLOCK_SIZE_REF)))
                rows_count = max(1, int(round(h_rect / BLOCK_SIZE_REF)))
                actual_cell_w = w_rect / cols_count
                actual_cell_h = h_rect / rows_count
                
                global_x = x_start + x
                global_y = SPAWN_Y1 + y
                screen_bbox = (global_x, global_y, w_rect, h_rect)
                
                for r in range(rows_count):
                    for c_idx in range(cols_count):
                        cx_rel = (c_idx * actual_cell_w) + (actual_cell_w / 2)
                        cy_rel = (r * actual_cell_h) + (actual_cell_h / 2)
                        mask_x = int(x + cx_rel)
                        mask_y = int(y + cy_rel)
                        mask_x = min(max(0, mask_x), mask.shape[1]-1)
                        mask_y = min(max(0, mask_y), mask.shape[0]-1)
                        if mask[mask_y, mask_x] > 0:
                            shape_matrix.append((r, c_idx))
                            
        if not shape_matrix:
            parsed_shapes.append(([], None))
        else:
            parsed_shapes.append((shape_matrix, screen_bbox))
            
    return parsed_shapes

if __name__ == "__main__":
    # Test capture
    img = capture_screen()
    if img is not None:
        print(f"Screenshot captured successfully. Shape: {img.shape}")
        cv2.imwrite("debug_capture.png", img)
        
        board = parse_board(img)
        print("Board State:")
        print(board)
        
        shapes_data = parse_shapes(img)
        print("Parsed Shapes:")
        for i, (shape, bbox) in enumerate(shapes_data):
            print(f"Slot {i+1}: {shape}, BBox: {bbox}")
    else:
        print("Failed to capture screenshot.")
