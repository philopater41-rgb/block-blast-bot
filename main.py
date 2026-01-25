import cv2
import numpy as np
import vision
import solver
import time

# Global state for mouse callback
needs_capture = False

def on_mouse(event, x, y, flags, param):
    global needs_capture
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if click is inside the "Capture" button
        # Button area: (50, 50) to (250, 100)
        if 50 <= x <= 250 and 50 <= y <= 100:
            needs_capture = True

def draw_ui(image, board, shapes, bboxes, solution):
    # Image is already the screenshot (or blank if init)
    
    # Draw "Capture" button
    cv2.rectangle(image, (50, 50), (250, 100), (200, 200, 200), -1)
    cv2.putText(image, "CAPTURE", (80, 85), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    if solution:
        # Colors: Step 1 (Red), Step 2 (Green), Step 3 (Blue)
        colors = [
            (0, 0, 255),   # Step 1: Red
            (0, 255, 0),   # Step 2: Green
            (255, 0, 0)    # Step 3: Blue
        ]
        
        # Draw highlights around source shapes
        for i, (shape_idx, r, c) in enumerate(solution):
            color = colors[i % len(colors)]
            bbox = bboxes[shape_idx]
            
            if bbox:
                bx, by, bw, bh = bbox
                # Draw thick border around the source shape
                cv2.rectangle(image, (bx, by), (bx+bw, by+bh), color, 5)
                # Add step number near the source shape
                cv2.putText(image, str(i+1), (bx, by-10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw moves on board (Reversed order for layering)
        reversed_solution = list(enumerate(solution))
        reversed_solution.reverse()
        
        for i, (shape_idx, r, c) in reversed_solution:
            shape = shapes[shape_idx]
            color = colors[i] 
            
            # Draw shape on board
            start_x = vision.BOARD_X
            start_y = vision.BOARD_Y
            cell_size = vision.CELL_SIZE
            
            for dr, dc in shape:
                bx = start_x + (c + dc) * cell_size
                by = start_y + (r + dr) * cell_size
                
                padding = 5
                cv2.rectangle(image, (bx+padding, by+padding), (bx+cell_size-padding, by+cell_size-padding), color, -1)
                cv2.putText(image, str(i+1), (bx+20, by+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

def main():
    global needs_capture
    print("Block Blast Bot Started")
    print("Click 'CAPTURE' button or press 'r' to refresh.")
    
    # Initial blank image
    ui_image = np.zeros((2400, 1080, 3), dtype=np.uint8)
    draw_ui(ui_image, np.zeros((8,8)), [], [], None)
    
    cv2.namedWindow("Block Blast Bot", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Block Blast Bot", on_mouse)
    
    # Resize window to fit screen
    cv2.resizeWindow("Block Blast Bot", 540, 1200)
    
    while True:
        cv2.imshow("Block Blast Bot", ui_image)
        key = cv2.waitKey(100) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r') or needs_capture:
            needs_capture = False # Reset flag
            print("Capturing...")
            
            try:
                img = vision.capture_screen()
                if img is None:
                    print("Capture failed.")
                    continue
                
                # Update UI image with new capture
                ui_image = img.copy()
                
                print("Analyzing...")
                board = vision.parse_board(img)
                shapes_data = vision.parse_shapes(img)
                
                # Unpack shapes and bboxes
                shapes = [s[0] for s in shapes_data]
                bboxes = [s[1] for s in shapes_data]
                
                # DEBUG: Print detected shapes
                print(f"Board:\n{board}")
                for i, shape in enumerate(shapes):
                    print(f"Slot {i+1}: {shape}")
                
                print("Solving...")
                best_sequence = solver.solve(board, shapes)
                
                if best_sequence:
                    print("Solution found!")
                    for move in best_sequence:
                        print(f"  -> Place shape {move[0]} at row={move[1]}, col={move[2]}")
                    draw_ui(ui_image, board, shapes, bboxes, best_sequence)
                else:
                    print("No solution found.")
                    print("=== DEBUG: No Solution ===")
                    print(f"Board:\n{board}")
                    print(f"Shapes: {shapes}")
                    for i, shape in enumerate(shapes):
                        if shape:
                            # Check if shape can be placed anywhere
                            can_place = False
                            for r in range(8):
                                for c in range(8):
                                    valid = True
                                    for dr, dc in shape:
                                        nr, nc = r + dr, c + dc
                                        if not (0 <= nr < 8 and 0 <= nc < 8):
                                            valid = False
                                            break
                                        if board[nr, nc] == 1:
                                            valid = False
                                            break
                                    if valid:
                                        can_place = True
                                        break
                                if can_place:
                                    break
                            print(f"Shape {i} ({len(shape)} cells): can_place={can_place}")
                        else:
                            print(f"Shape {i}: EMPTY")
                    print("=== END DEBUG ===")
                    cv2.putText(ui_image, "No Solution Found!", (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
                    # Ensure button is redrawn
                    draw_ui(ui_image, board, shapes, bboxes, None) 
                    
            except Exception as e:
                print(f"ERROR: An exception occurred: {e}")
                import traceback
                traceback.print_exc()
                cv2.putText(ui_image, "ERROR! Check Console", (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                draw_ui(ui_image, np.zeros((8,8)), [], [], None) 
                
            # Refresh window
            cv2.imshow("Block Blast Bot", ui_image)

if __name__ == "__main__":
    main()
