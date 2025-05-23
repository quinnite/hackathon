from PyQt5 import QtWidgets, QtCore
from gui import Ui_MainWindow
from logic import ImageProcessor
from PyQt5.QtGui import QIcon
import cv2  # Needed for save function

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.setWindowIcon(QIcon("camera.ico"))
        self.ui.setupUi(self)

        self.processor = ImageProcessor()

        # Button clicks
        self.ui.uploadImage.clicked.connect(self.load_image)
        self.ui.saveImage.clicked.connect(self.save_image)
        self.ui.resetImage.clicked.connect(self.reset_image)

        # Checkbox toggles
        self.ui.grayscale.toggled.connect(lambda checked: self.toggle_transform("grayscale", checked))
        self.ui.medianBlur.toggled.connect(lambda checked: self.toggle_transform("medianBlur", checked))
        self.ui.cannyEdge.toggled.connect(lambda checked: self.toggle_transform("cannyEdge", checked))
        self.ui.erosion.toggled.connect(lambda checked: self.toggle_transform("erosion", checked))
        self.ui.gaussianBlur.toggled.connect(lambda checked: self.toggle_transform("gaussianBlur", checked))
        self.ui.sobelEdge.toggled.connect(lambda checked: self.toggle_transform("sobelEdge", checked))
        self.ui.rotate.toggled.connect(lambda checked: self.toggle_transform("rotate", checked))
        self.ui.flip.toggled.connect(lambda checked: self.toggle_transform("flip", checked))

        # Sliders
        self.ui.brightnessSlider.valueChanged.connect(self.set_brightness)
        self.ui.contrastSlider.valueChanged.connect(self.set_contrast)

    def load_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if path:
            success = self.processor.load_image(path)
            if success:
                self.update_image_label()

    def save_image(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")
        if path and self.processor.processed_image is not None:
            cv2.imwrite(path, self.processor.processed_image)

    def reset_image(self):
        self.processor.reset()

        # Reset UI toggles/sliders to defaults
        for checkbox in [
            self.ui.grayscale,
            self.ui.medianBlur,
            self.ui.cannyEdge,
            self.ui.erosion,
            self.ui.gaussianBlur,
            self.ui.sobelEdge,
            self.ui.rotate,
            self.ui.flip,
        ]:
            checkbox.setChecked(False)

        self.ui.brightnessSlider.setValue(0)
        self.ui.contrastSlider.setValue(0)
        self.update_image_label()

    def toggle_transform(self, name, checked):
        self.processor.set_transform(name, checked)
        self.update_image_label()

    def set_brightness(self, val):
        self.processor.set_brightness(val)
        self.update_image_label()

    def set_contrast(self, val):
        self.processor.set_contrast(val)
        self.update_image_label()

    def update_image_label(self):
        pixmap = self.processor.get_qpixmap()
        if pixmap:
            self.ui.imageLabel.setPixmap(
                pixmap.scaled(self.ui.imageLabel.width(), self.ui.imageLabel.height(), QtCore.Qt.KeepAspectRatio)
            )

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    with open("style.qss", "r") as f:
        style = f.read()
    app.setStyleSheet(style)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())
