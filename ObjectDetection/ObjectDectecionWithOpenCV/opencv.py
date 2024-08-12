import sys
import os
import cv2
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QHBoxLayout, QMessageBox
from ultralytics import YOLO
import openpyxl
from openpyxl import load_workbook
import xlwings as xw
from ui import UiDialog  # Import the generated UI class

# Constants
WIDTH = 1080
HEIGHT = 720

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    frame_captured_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.cap = cv2.VideoCapture(0)  # Use default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.current_frame = None

    def run(self):
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                qt_img = self.convert_cv_qt(frame)
                self.current_frame = frame
                self.change_pixmap_signal.emit(qt_img)

    def stop(self):
        self._run_flag = False
        self.cap.release()  # Release the camera
        self.wait()  # Ensure the thread has finished

    def convert_cv_qt(self, cv_img):
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        return p

class TehseenCode(QDialog):
    def __init__(self):
        super(TehseenCode, self).__init__()
        self.ui = UiDialog()
        self.ui.setup_ui(self)
        
        # Initialization
        self.logic = 0
        self.value = 1
        self.img_folder = "img"
        os.makedirs(self.img_folder, exist_ok=True)
        self.thread = None
        self.model = None
        self.total_detected_objects = 0
        self.SUMLIST = []
        
        # Connect buttons
        self.ui.select_excel_btn.clicked.connect(self.open_excel_file_dialog)
        self.ui.camera_btn.clicked.connect(self.start_video)
        self.ui.capture_btn.clicked.connect(self.CaptureClicked)
        self.ui.quit_btn.clicked.connect(self.quitClicked)
        self.ui.upload_btn.clicked.connect(self.uploadClicked)
        self.ui.undo_btn.clicked.connect(self.resetCounter)
        self.ui.send_btn.clicked.connect(self.send_data_to_excel)
        
        self.ui.text_browser.setText('Press "CAMERA" to connect with camera')
        self.ui.processed_img_label.setScaledContents(True)
        
        # Setup UI layout
        layout = QHBoxLayout()
        self.ui.frame_right.setLayout(layout)
        layout.addWidget(self.ui.img_label)
        layout.addWidget(self.ui.processed_img_label)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Initialize YOLO model
        self.setup_yolo_model()
        
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
        self.ui.img_label.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot()
    def frameCaptured(self):
        self.ui.text_browser.setText('Image captured')

    def CaptureClicked(self):
        if self.thread is not None and self.thread.current_frame is not None:
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
            # Display the uploaded image on the left label
            self.display_image(fileName, self.ui.img_label)  
            self.detect_image_and_display(fileName)

    def detect_image_and_display(self, image_path):
        detected_image_path = self.detect_image(image_path)
        # Update the processed image on the right label
        self.update_processed_image(detected_image_path)  
        
        # Send total_detected_objects to specfic excel cell automation 
        self.send_data_to_excel()
        
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
        self.ui.text_browser.setText(f'Total: {elements} = {self.total_detected_objects}')
        self.ui.total_objects_label.setText(f'Total Objects: {self.total_detected_objects}')
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
        label.setPixmap(QPixmap.fromImage(self.convert_cv_qt(cv_img)))

    def update_processed_image(self, img_path):
        self.display_image(img_path, self.ui.processed_img_label)
        
    def quitClicked(self):
        if self.thread is not None:
            self.resetCounter()
            self.thread.stop()
        QApplication.quit()

    def resetCounter(self):
        reply = QMessageBox.question(self, 'Confirm Undo', 'Are you sure you want to undo the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                remove_lastcount = self.SUMLIST.pop()
                SUMLIST = remove_lastcount
                elements = " + ".join(map(str, self.SUMLIST))
                self.total_detected_objects = sum(self.SUMLIST)
                self.ui.text_browser.setText(f'Total: {elements} = {self.total_detected_objects}')
                self.ui.total_objects_label.setText(f'Total Objects: {self.total_detected_objects}')
                self.send_data_to_excel()
            except:
                QMessageBox.information(self, "Error", "Can Not Undo") 
                print("List empty: Can't Undo")
        
    def convert_cv_qt(self, cv_img):
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        return p
    
    # Choose a excel file 
    def open_excel_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options)
        if file_path:
            # If a file is selected, open it
            self.open_excel_file(file_path)
    
    # Open an Excel file and activate it for interaction    
    def open_excel_file(self, file_path):
        # Create an instance of Excel and make it visible
        self.excel_app = xw.App(visible=True)
        
        # Open the specified workbook
        self.excel_wb = self.excel_app.books.open(file_path)
        self.excel_sheet = self.excel_wb.sheets.active
        
        # Check if 'Book1' is open and close it if it exists
        try:
            for book in self.excel_app.books:
                if book.name == 'Book1':
                    book.close()
                    break
        except:
            pass 

    # Get the currently selected cell in the active Excel sheet and update the active sheet reference
    def get_selected_cell(self):
        # Check if the 'excel_wb' attribute exists
        if not hasattr(self, 'excel_wb') or self.excel_wb is None:
            QMessageBox.critical(self, "Error", "Don't have any opened Excel file")
            return None
        
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
            QMessageBox.critical(self, "Error", "Error when getting selected cell") 

    # Write the total_detected_objects to the selected cell in Excel
    def send_data_to_excel(self):
        try:
            # Add a small delay to ensure Excel has enough time to register the cell selection
            QTimer.singleShot(100, self._write_data_to_excel)
        except Exception as e:
            print(f"Error writing data to Excel: {e}")
            self.ui.text_browser.setText('Failed to write data to Excel')
            
    def _write_data_to_excel(self):
        selected_cell = self.get_selected_cell()
        if selected_cell:
            try:
                self.excel_sheet.range(selected_cell).value = self.total_detected_objects
                self.excel_wb.save()  # Save the changes
                self.ui.text_browser.setText(f'Data written to {selected_cell}')
            except Exception as e:
                print(f"Error writing data to Excel: {e}")
                self.ui.text_browser.setText('Failed to write data to Excel')
        else:
            self.ui.text_browser.setText('No cell selected in Excel')
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    code = TehseenCode()
    code.setWindowTitle('PNJP Automatic Counting')
    code.show()
    sys.exit(app.exec_())
