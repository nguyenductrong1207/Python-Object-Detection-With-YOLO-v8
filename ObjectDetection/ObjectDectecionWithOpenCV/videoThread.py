import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QImage

# Constants
WIDTH = 1080
HEIGHT = 720

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    frame_captured_signal = pyqtSignal()
    camera_failed_signal = pyqtSignal()  # Signal for camera initialization failure

    def __init__(self, camera_index=0):
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(camera_index)  # Use the selected camera index
        if not self.cap.isOpened():  # Check if the camera failed to open
            self.camera_failed_signal.emit()
            return
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.current_frame = None

    def run(self):
        # Ensure the camera is opened before running the loop
        if not self.cap.isOpened():  
            return
        
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                qt_img = self.convert_cv_qt(frame)
                self.current_frame = frame
                self.change_pixmap_signal.emit(qt_img)

    def stop(self):
        self._run_flag = False
        # Ensure the camera is only released if it was opened
        if self.cap.isOpened():  
            self.cap.release()
        self.wait()  # Ensure the thread has finished

    def convert_cv_qt(self, cv_img):
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        return p
