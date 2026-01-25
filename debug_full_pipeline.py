import cv2
import numpy as np
import vision
import solver

def debug_pipeline(image_path):
    print(f"--- Debugging Pipeline for {image_path} ---")
    
    # 1. Load Image
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Could not read image.")
        return

    print(f"Image Size: {img.shape}")

    # 2. Parse Board
    print("\n[Vision] Parsing Board...")
    board = vision.parse_board(img)
    print("Board State:")
    print(board)
    
    # Count filled cells
    filled = np.sum(board)
    print(f"Filled cells: {filled}/64")

    # 3. Parse Shapes
    print("\n[Vision] Parsing Shapes...")
    theme = vision.detect_theme(img)
    print(f"Detected Theme: {theme}")
    
    shapes_data = vision.parse_shapes(img)
    shapes = [s[0] for s in shapes_data]
    
    print(f"Found {len(shapes)} slots.")
    for i, shape in enumerate(shapes):
        print(f"Slot {i+1}: {shape}")
        
    # 4. Solve
    print("\n[Solver] Solving...")
    try:
        sequence = solver.solve(board, shapes)
        print(f"Solution Sequence: {sequence}")
        
        if not sequence:
            print("FAILURE: No solution found.")
        else:
            print("SUCCESS: Solution found!")
            for move in sequence:
                print(f"  -> Place shape {move[0]} at row={move[1]}, col={move[2]}")
                
    except Exception as e:
        print(f"CRASH: Solver failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    image_path = r"C:/Users/philo/.gemini/antigravity/brain/6fc9f17a-e3ce-4792-9bd1-0e3782130009/uploaded_image_1767560720028.png"
    debug_pipeline(image_path)
