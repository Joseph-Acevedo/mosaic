from PIL import Image
import cv2
import numpy as np

img = np.full((200, 200, 3), (0, 0, 0), np.uint8)
red_img = np.full(img.shape, (0,0,255), np.uint8)
fused_img = cv2.addWeighted(img, 0.4, red_img, 0.6, 0)
cv2.imshow("tinged red", fused_img)
cv2.waitKey(0)