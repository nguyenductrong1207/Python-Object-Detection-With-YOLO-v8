import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QImage

# Constants for the video resolution
WIDTH = 1080
HEIGHT = 720

class VideoThread(QThread):
    # Signal to emit a new frame as a QImage for GUI display
    change_pixmap_signal = pyqtSignal(QImage)
    
    # Signal to notify when a frame is captured
    frame_captured_signal = pyqtSignal()
    
    # Signal to notify if the camera fails to initialize
    camera_failed_signal = pyqtSignal()  

    def __init__(self, camera_index=0):
        super().__init__()
        self._run_flag = True
        
        # Initialize video capture with the specified camera index
        self.cap = cv2.VideoCapture(camera_index)  
        
        # Check if the camera was opened successfully
        if not self.cap.isOpened(): 
            # Emit failure signal if the camera cannot be opened 
            self.camera_failed_signal.emit()
            return
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.current_frame = None # Placeholder for the current video frame

    def run(self):
        # Ensure the camera is opened before running the loop
        if not self.cap.isOpened():  
            return
        
        while self._run_flag:
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            if ret:
                qt_img = self.convert_cv_qt(frame)
                self.current_frame = frame
                
                # Emit the frame as a QImage to update the display
                self.change_pixmap_signal.emit(qt_img)

    # Convert the frame to QImage format for PyQt display
    def convert_cv_qt(self, cv_img):
        # Convert from BGR to RGB format required by QImage
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w # Calculate the number of bytes per line
        # Convert the image data to QImage format
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # Scale the image to fit the display area while keeping the aspect ratio
        p = convert_to_qt_format.scaled(790, 610, QtCore.Qt.KeepAspectRatio)
        return p

    def stop(self):
        self._run_flag = False
        # Release the camera only if it was opened
        if self.cap.isOpened():  
            self.cap.release()
        self.wait()  # Ensure the thread has finished


