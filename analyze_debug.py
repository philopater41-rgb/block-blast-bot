import cv2
import numpy as np

# Load the shape_area image
img = cv2.imread(r"C:\Users\philo\.gemini\antigravity\brain\6fc9f17a-e3ce-4792-9bd1-0e3782130009\uploaded_image_1767557370249.png")

h, w, _ = img.shape
print(f"Image size: {w}x{h}")

# Convert to HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Sample the dark blue shape (center of image, upper area)
center_y = h // 4  # Shape is in upper quarter
center_x = w // 2  # Shape is in center

# Sample 30x30 area from the shape
sample = hsv[center_y-15:center_y+15, center_x-15:center_x+15]
avg_hsv = np.mean(sample, axis=(0, 1))
print(f"Shape HSV: H={avg_hsv[0]:.1f}, S={avg_hsv[1]:.1f}, V={avg_hsv[2]:.1f}")

# Sample background (bottom left - clearly background)
bg_sample = hsv[h-50:h-20, 20:50]
bg_hsv = np.mean(bg_sample, axis=(0, 1))
print(f"Background HSV: H={bg_hsv[0]:.1f}, S={bg_hsv[1]:.1f}, V={bg_hsv[2]:.1f}")

# Also sample the text at bottom (might be detected as noise)
text_sample = hsv[h-30:h-5, w//2-50:w//2+50]
text_hsv = np.mean(text_sample, axis=(0, 1))
print(f"Text area HSV: H={text_hsv[0]:.1f}, S={text_hsv[1]:.1f}, V={text_hsv[2]:.1f}")

v_channel = hsv[:,:,2]
s_channel = hsv[:,:,1]

# Test thresholds
print("\n--- Testing Thresholds ---")

# V < 220 (current)
_, mask1 = cv2.threshold(v_channel, 220, 255, cv2.THRESH_BINARY_INV)
print(f"V < 220: {np.count_nonzero(mask1)} white pixels ({100*np.count_nonzero(mask1)/(h*w):.1f}%)")

# V < 230
_, mask2 = cv2.threshold(v_channel, 230, 255, cv2.THRESH_BINARY_INV)
print(f"V < 230: {np.count_nonzero(mask2)} white pixels ({100*np.count_nonzero(mask2)/(h*w):.1f}%)")

# S > 200 AND V < 235
_, mask_s = cv2.threshold(s_channel, 200, 255, cv2.THRESH_BINARY)
_, mask_v = cv2.threshold(v_channel, 235, 255, cv2.THRESH_BINARY_INV)
mask3 = cv2.bitwise_and(mask_s, mask_v)
print(f"S > 200 AND V < 235: {np.count_nonzero(mask3)} white pixels ({100*np.count_nonzero(mask3)/(h*w):.1f}%)")

# Combined
mask_combined = cv2.bitwise_or(mask1, mask3)
print(f"Combined (V<220 OR (S>200 AND V<235)): {np.count_nonzero(mask_combined)} white pixels")

# Save test masks
cv2.imwrite("test_mask_v220.png", mask1)
cv2.imwrite("test_mask_combined.png", mask_combined)

print("\nSaved test masks.")
