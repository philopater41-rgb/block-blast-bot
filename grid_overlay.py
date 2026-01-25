import cv2
import numpy as np

# Load user's uploaded image
img = cv2.imread(r"C:\Users\philo\.gemini\antigravity\brain\6fc9f17a-e3ce-4792-9bd1-0e3782130009\uploaded_image_1767565014031.png")

h, w, _ = img.shape
print(f"Image size: {w}x{h}")

# Draw a marker grid to visually identify the board
debug = img.copy()

# Draw horizontal lines every 50 pixels with labels
for y in range(0, h, 50):
    cv2.line(debug, (0, y), (w, y), (0, 255, 255), 1)
    cv2.putText(debug, str(y), (5, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

# Draw vertical lines every 50 pixels with labels
for x in range(0, w, 50):
    cv2.line(debug, (x, 0), (x, h), (0, 255, 255), 1)
    cv2.putText(debug, str(x), (x+2, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

cv2.imwrite("debug_grid_overlay.png", debug)
print("Saved: debug_grid_overlay.png")
print("Open this image to see pixel coordinates of board edges")
