from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, Qt
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
            try:
                # Attempt to capture a frame
                grab_result = self.basler_camera.GrabOne(120000)  # 120000ms timeout
                if grab_result.GrabSucceeded():
                    image = grab_result.Array
                    qt_img = self.convert_cv_qt(image)
                    self.change_pixmap_signal.emit(qt_img)  # Emit the frame as a QImage
                else:
                    print("Frame capture failed. Grab did not succeed.")
            except pylon.TimeoutException as e:
                print(f"Error: Timeout occurred while grabbing frame: {str(e)}")
                break  # Optionally, break the loop if you don't want to keep retrying
            except Exception as e:
                print(f"Error: An unexpected error occurred: {str(e)}")
                break  # Break the loop to stop further processing

    def stop(self):
        self._run_flag = False
        self.basler_camera.StopGrabbing()
        self.wait()

    def convert_cv_qt(self, cv_img):
        """Convert from an OpenCV image to a QPixmap which is suitable for PyQt display."""
        if len(cv_img.shape) == 2:
            # Grayscale image, it doesn't have a color channel
            h, w = cv_img.shape
            qt_img = QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8)
        else:
            # Color image, assumed to be in BGR format
            rgb_image = cv_img[:, :, ::-1].copy()  # Convert BGR to RGB
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Scale the QImage to fit the designated UI label size
        scaled_img = qt_img.scaled(790, 610, QtCore.Qt.KeepAspectRatio)
        return scaled_img
