from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
from pypylon import pylon

class BaslerVideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, basler_camera):
        super().__init__()
        self._run_flag = True
        self.basler_camera = basler_camera

    def run(self):
        while self._run_flag:
            grab_result = self.basler_camera.GrabOne(1000)  # Capture a frame
            if grab_result.GrabSucceeded():
                image = grab_result.Array
                qt_img = self.convert_cv_qt(image)
                self.change_pixmap_signal.emit(qt_img)  # Emit the frame as a QImage

    def stop(self):
        self._run_flag = False
        self.wait()

    def convert_cv_qt(self, cv_img):
        """Convert from OpenCV's BGR image format to Qt's QImage."""
        rgb_image = cv_img[:, :, ::-1].copy()  # Convert BGR to RGB
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_img = qt_img.scaled(790, 610, QtCore.Qt.KeepAspectRatio)
        return scaled_img
