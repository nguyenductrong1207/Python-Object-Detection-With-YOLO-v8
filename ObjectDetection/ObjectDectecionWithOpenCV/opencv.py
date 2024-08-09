# -*- coding: utf-8 -*-

import sys
import cv2
import os
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QHBoxLayout
from ui import Ui_Dialog  # Import the generated UI class
from ultralytics import YOLO
from datetime import datetime
import openpyxl
from openpyxl import load_workbook
import xlwings as xw

WIDTH = 1080
HEIGHT = 720

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    frame_captured_signal = pyqtSignal()

    def __init__(self):
        # super().__init__()
        # self._run_flag = True
        # self.picam2 = Picamera2()
        # self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (WIDTH,HEIGHT), "format": "RGB888"}))
        # self.picam2.set_controls({"AwbEnable":1,
        #     "AwbMode": 0,  # Cân bằng trắng tự động (1 là giá trị tương ứng với chế độ Auto)
        #     #"Brightness": 0.5,  # Độ sáng trung bình (giá trị float)
        #     #"Contrast": 1.0,    # Tăng độ tương phản (giá trị float)
        #     #"Saturation": 1.0,  # Tăng độ bão hòa (giá trị float)
        #     "Sharpness": 1.0    # Tăng độ sắc nét (giá trị float)
        #     })
        # self.picam2.start()
        # self.current_frame = None
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(0)  # Use default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.current_frame = None

    def run(self):
        while self._run_flag:
            # frame = self.picam2.capture_array()
            # qt_img = self.convert_cv_qt(frame)
            # self.current_frame = frame
            # self.change_pixmap_signal.emit(qt_img)
            
            ret, frame = self.cap.read()
            if ret:
                qt_img = self.convert_cv_qt(frame)
                self.current_frame = frame
                self.change_pixmap_signal.emit(qt_img)

    def stop(self):
        self._run_flag = False
        # self.picam2.stop()
        # self.picam2.close()
        # self.wait()  # Ensure the thread has finished
        
        self.cap.release()  # Release the camera
        self.wait()  # Ensure the thread has finished

    def convert_cv_qt(self, cv_img):
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        return p

class TehseenCode(QDialog):
    def __init__(self):
        super(TehseenCode, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        self.logic = 0
        self.value = 1
        self.img_folder = "img"
        os.makedirs(self.img_folder, exist_ok=True)
        
        self.ui.CAMERA.clicked.connect(self.start_video)
        self.ui.TEXT.setText('Press "CAMERA" to connect with camera')
        self.ui.CAPTURE.clicked.connect(self.CaptureClicked)
        self.ui.QUIT.clicked.connect(self.quitClicked)
        self.ui.UPLOAD.clicked.connect(self.uploadClicked)
        self.ui.UNDO.clicked.connect(self.resetCounter)
        self.thread = None
        self.model = None
        self.setup_yolo_model()
        self.ui.processedImgLabel.setScaledContents(True)
        self.total_detected_objects = 0
        self.SUMLIST = []

        # Tạo một layout ngang để chứa label camera và label mới
        layout = QHBoxLayout()
        self.ui.frameRight.setLayout(layout)

        # Thêm label camera và label mới vào layout
        layout.addWidget(self.ui.imgLabel)
        layout.addWidget(self.ui.processedImgLabel)

        # Thiết lập layout để căn giữa phần tử
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Initialize variables for Excel handling
        # self.excel_app = None
        # self.excel_wb = None
        # self.excel_sheet = None
        
        # Connect Send button to the new method
        self.ui.SEND.clicked.connect(self.send_data_to_excel)

    # def setup_yolo_model(self):
    #     folder_path = "runs/detect"
    #     self.latest_trainedfolder, _ = self.get_latest_modified_train_folder(folder_path, 'train')
    #     self.latest_trainedfolder = "runs/detect/train75"
    #     self.model = YOLO(task='detect', model=f"{self.latest_trainedfolder}/weights/best.pt")
        
    def setup_yolo_model(self):
        folder_path = os.path.join(os.path.dirname(__file__), 'runs', 'detect')
        self.latest_trainedfolder, _ = self.get_latest_modified_train_folder(folder_path, 'train')
        if self.latest_trainedfolder:
            model_path = os.path.join(self.latest_trainedfolder, "weights", "best.pt")
            print(f"Model path: {model_path}")  # Print path for debugging
            if os.path.isfile(model_path):
                self.model = YOLO(task='detect', model=model_path)
            else:
                print(f"Error: Model file not found at {model_path}")
        else:
            print("Error: No valid training folder found.")

    def get_latest_modified_train_folder(self, folder_path, subname):
        try:
            folders = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)) and subname in f.lower()]
            if not folders:
                return None, None
            latest_folder = max(folders, key=os.path.getmtime)
            latest_time = os.path.getmtime(latest_folder)
            latest_time_formatted = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')
            return latest_folder, latest_time_formatted
        except Exception as e:
            print(f"Error: {e}")
            return None, None

    @pyqtSlot()
    def start_video(self):
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.frame_captured_signal.connect(self.frameCaptured)
        self.thread.start()

    @pyqtSlot(QImage)
    def update_image(self, img):
        self.ui.imgLabel.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot()
    def frameCaptured(self):
        self.ui.TEXT.setText('Image captured')

    def CaptureClicked(self):
        if self.thread is not None and self.thread.current_frame is not None:
            # cv_img = self.thread.current_frame
            # img_path = f"{self.img_folder}/image{self.value}.jpg"
            # cv2.imwrite(img_path, cv_img)
            # self.value += 1
            # self.detect_image_and_display(img_path)
            # # Restart the video thread to resume the video stream
            # self.thread.stop()
            
            # Define the path for the image
            img_path = os.path.join(self.img_folder, f"image{self.value}.jpg")
            
            # Save the current frame
            cv2.imwrite(img_path, self.thread.current_frame)
            self.value += 1
            
            # Process the saved image
            self.detect_image_and_display(img_path)
            
            # Restart the video thread to resume the video stream
            self.thread.stop()
            
    def uploadClicked(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if fileName:
            self.display_image(fileName, self.ui.imgLabel)  # Display the uploaded image on the left label
            self.detect_image_and_display(fileName)

    def detect_image_and_display(self, image_path):
        detected_image_path = self.detect_image(image_path)
        self.update_processed_image(detected_image_path)  # Update the processed image on the right label
        #self.TEXT.setText('Image detected and displayed')

    def detect_image(self, image_path):
        output_dir = 'annotated_images'
        os.makedirs(output_dir, exist_ok=True)
        
        results = self.model(source=image_path, imgsz=800, conf=0.55, save=False, show_labels=True)
        detected_image_path = self.draw_bounding_boxes(image_path, results, output_dir)
        # Update the total detected objects counter
        num_detected_objects = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
        self.total_detected_objects += num_detected_objects
        self.SUMLIST.append(num_detected_objects)
        elements = " + ".join(map(str, self.SUMLIST))
        self.ui.TEXT.setText(f'Total: {elements} = {self.total_detected_objects}')
        self.ui.totalObjectsLabel.setText(f'Total Objects: {self.total_detected_objects}')
        return detected_image_path

    def draw_bounding_boxes(self, image_path, results, output_dir):
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Unable to open image file {image_path}")
            return image_path

        height, width, _ = img.shape
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = width / 1500
        font_thickness = 3
        text_color = (0, 0, 255)
        bg_color = (0, 0, 0)

        for idx, box in enumerate(results[0].boxes):
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            label = f"{idx + 1}"
            text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
            text_x = x1 + 5
            text_y = y1 - 10 if y1 - 10 > 0 else y1 + text_size[1] + 10

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (text_x - 5, text_y - text_size[1] - 5),
                          (text_x + text_size[0] + 5, text_y + 5), bg_color, -1)
            cv2.putText(img, label, (text_x, text_y), font, font_scale, text_color, font_thickness)

        num_boxes = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
        font_scale = width / 500
        title = f"PNJP detects: {num_boxes} objects"
        text_size = cv2.getTextSize(title, font, font_scale, font_thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = text_size[1] + 10
        text_color = (255, 255, 255)
        bg_color = (0, 0, 0)
        cv2.rectangle(img, (text_x - 10, text_y - text_size[1] - 10), 
                      (text_x + text_size[0] + 10, text_y + 10), bg_color, -1)
        cv2.putText(img, title, (text_x, text_y), font, font_scale, text_color, font_thickness)

        output_filename = f'annotated_{os.path.basename(image_path)}'
        output_path = os.path.join(output_dir, output_filename)
        cv2.imwrite(output_path, img)
        print(f"Annotated image saved at {output_path}")
        return output_path

    def display_image(self, image_path, label):
        cv_img = cv2.imread(image_path)
        qt_img = self.convert_cv_qt(cv_img)
        label.setPixmap(QPixmap.fromImage(qt_img))

    def update_processed_image(self, img_path):
        self.display_image(img_path, self.ui.processedImgLabel)
        
    def quitClicked(self):
        if self.thread is not None:
            self.resetCounter()
            self.thread.stop()
        QApplication.quit()

    def resetCounter(self):
        try:
                remove_lastcount = self.SUMLIST.pop()
                SUMLIST = remove_lastcount
                elements = " + ".join(map(str, self.SUMLIST))
                self.total_detected_objects = sum(self.SUMLIST)
                self.ui.TEXT.setText(f'Total: {elements} = {self.total_detected_objects}')
                self.ui.totalObjectsLabel.setText(f'Total Objects: {self.total_detected_objects}')
        except:
                print("List empty")
        
    def convert_cv_qt(self, cv_img):
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        return p
        
    def open_excel_file(self, file_path):
        """Open an Excel file and activate it for interaction."""
        # Create an instance of Excel and make it visible
        self.excel_app = xw.App(visible=True)
        
        # Open the specified workbook first
        self.excel_wb = self.excel_app.books.open(file_path)
        self.excel_sheet = self.excel_wb.sheets.active
        
        # Check if 'Book1' is open and close it if it exists
        try:
            for book in self.excel_app.books:
                if book.name == 'Book1':
                    book.close()
                    break
        except:
            pass  # If there's no 'Book1', just continue

    def get_selected_cell(self):
        """Get the currently selected cell in the active Excel sheet and update the active sheet reference."""
        if self.excel_wb:
            try:
                # Update the active sheet to the currently active one
                self.excel_sheet = self.excel_wb.sheets.active
                
                # Access the last selected range directly using the API
                selection = self.excel_sheet.api.Application.Selection
                
                # Convert the selection to an address format
                address = selection.Address
                print(f"Selected cell address: {address}")  # For debugging
                return address
            except Exception as e:
                print(f"Error getting selected cell: {e}")
                return None
        return None

    def send_data_to_excel(self):
        """Write the total_detected_objects to the selected cell in Excel."""
        try:
            # Add a small delay to ensure Excel has enough time to register the cell selection
            QTimer.singleShot(100, self._write_data_to_excel)
        except Exception as e:
            print(f"Error writing data to Excel: {e}")
            self.ui.TEXT.setText('Failed to write data to Excel')
    def _write_data_to_excel(self):
        selected_cell = self.get_selected_cell()
        if selected_cell:
            try:
                self.excel_sheet.range(selected_cell).value = self.total_detected_objects
                self.excel_wb.save()  # Save the changes
                self.ui.TEXT.setText(f'Data written to {selected_cell}')
            except Exception as e:
                print(f"Error writing data to Excel: {e}")
                self.ui.TEXT.setText('Failed to write data to Excel')
        else:
            self.ui.TEXT.setText('No cell selected in Excel')
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TehseenCode()
    window.setWindowTitle('PNJP Automatic Counting')
    
    # Open the Excel file when starting the app
    excel_file_path = "D:/Github/Object-Detection-With-Python/ObjectDetection/OpenCV/test.xlsx"
    window.open_excel_file(excel_file_path)
    
    window.show()
    sys.exit(app.exec_())
