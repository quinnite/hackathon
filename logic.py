import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.processed_image = None

        self.transforms = {
            "grayscale": False,
            "medianBlur": False,
            "cannyEdge": False,
            "erosion": False,
            "gaussianBlur": False,
            "sobelEdge": False,
            "rotate": False,
            "flip": False,
        }

        self.brightness = 0
        self.contrast = 0

    def load_image(self, filepath):
        img = cv2.imread(filepath)
        if img is not None:
            self.original_image = img
            self.processed_image = img.copy()
            return True
        return False

    def reset(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            for key in self.transforms:
                self.transforms[key] = False
            self.brightness = 0
            self.contrast = 0

    def set_transform(self, name, enabled):
        if name in self.transforms:
            self.transforms[name] = enabled

    def set_brightness(self, val):
        self.brightness = val

    def set_contrast(self, val):
        self.contrast = val

    def apply_all(self):
        if self.original_image is None:
            return None

        img = self.original_image.copy()

        if self.transforms["grayscale"]:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        if self.transforms["medianBlur"]:
            img = cv2.medianBlur(img, 5)

        if self.transforms["gaussianBlur"]:
            img = cv2.GaussianBlur(img, (7,7), 0)

        if self.transforms["cannyEdge"]:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        if self.transforms["erosion"]:
            kernel = np.ones((3,3), np.uint8)
            img = cv2.erode(img, kernel, iterations=1)

        if self.transforms["sobelEdge"]:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, 3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, 3)
            sobel = cv2.magnitude(sobelx, sobely)
            sobel = np.uint8(np.clip(sobel, 0, 255))
            img = cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)

        if self.transforms["rotate"]:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        if self.transforms["flip"]:
            img = cv2.flip(img, 1)

        img = self.apply_brightness_contrast(img, self.brightness, self.contrast)

        self.processed_image = img
        return img

    @staticmethod
    def apply_brightness_contrast(input_img, brightness=0, contrast=0):
        img = input_img.copy()

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            img = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)

        if contrast != 0:
            f = 131*(contrast + 127)/(127*(131 - contrast))
            alpha_c = f
            gamma_c = 127*(1 - f)
            img = cv2.addWeighted(img, alpha_c, img, 0, gamma_c)

        return img

    def get_qpixmap(self):
        self.apply_all()
        if self.processed_image is None:
            return None

        img = self.processed_image

        if len(img.shape) == 3 and img.shape[2] == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(qimg)
        elif len(img.shape) == 2:
            h, w = img.shape
            bytes_per_line = w
            qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
            return QPixmap.fromImage(qimg)
        return None