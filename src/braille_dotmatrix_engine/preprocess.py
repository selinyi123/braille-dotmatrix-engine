import cv2
import numpy as np

def float01(img):
    arr = np.asarray(img, dtype=np.float32)
    if arr.size and arr.max() > 1.0:
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)

def apply_clahe_lab(img_bgr, clip_limit, grid_size):
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
    l2 = clahe.apply(l)
    return cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)
