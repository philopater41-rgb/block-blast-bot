import cv2
import numpy as np

# Load the image
img = cv2.imread(r"C:\Users\philo\.gemini\antigravity\brain\6fc9f17a-e3ce-4792-9bd1-0e3782130009\uploaded_image_1767552552269.png")
h, w, _ = img.shape

# Shape area (bottom 25% - starting from 72% as tuned)
spawn_y = int(h * 0.72)
shape_area = img[spawn_y:, :]

# Convert to HSV
hsv = cv2.cvtColor(shape_area, cv2.COLOR_BGR2HSV)

# Value channel - shapes are DARKER than background
v_channel = hsv[:,:,2]

# The KEY insight: Shapes (blocks) are DARKER (V < 180) than Background (V > 220)
# Let's find shapes by looking for DARK areas
_, mask_dark = cv2.threshold(v_channel, 180, 255, cv2.THRESH_BINARY_INV)

# Also try to detect BRIGHT cyan shapes (Saturation + Value)
# High Saturation (> 200) with High Value (> 200) = Cyan shapes
s_channel = hsv[:,:,1]
_, mask_bright_s = cv2.threshold(s_channel, 200, 255, cv2.THRESH_BINARY)
_, mask_bright_v = cv2.threshold(v_channel, 200, 255, cv2.THRESH_BINARY)
mask_bright = cv2.bitwise_and(mask_bright_s, mask_bright_v)

# Combined: Dark OR Bright
mask_combined = cv2.bitwise_or(mask_dark, mask_bright)

# Clean up
kernel = np.ones((5,5), np.uint8)
mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel)
mask_combined = cv2.dilate(mask_combined, kernel, iterations=1)

# Save
cv2.imwrite("debug_mask_dark.png", mask_dark)
cv2.imwrite("debug_mask_bright.png", mask_bright)
cv2.imwrite("debug_mask_combined.png", mask_combined)

# Find contours
contours, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Found {len(contours)} contours")

# Draw
debug = shape_area.copy()
cv2.drawContours(debug, contours, -1, (0, 255, 0), 2)
cv2.imwrite("debug_contours_new.png", debug)

# Analyze each contour
slot_width = w // 3
for i, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    x, y, cw, ch = cv2.boundingRect(cnt)
    slot = x // slot_width
    print(f"Contour {i}: Area={area}, X={x}, Y={y}, W={cw}, H={ch}, Slot={slot}")

print("\nDone!")
