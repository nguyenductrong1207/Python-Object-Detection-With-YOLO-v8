import sys
import os
import cv2
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QHBoxLayout, QMessageBox, QDesktopWidget 
from ultralytics import YOLO
import openpyxl
from openpyxl import load_workbook
import xlwings as xw
from ui import UiDialog  # Import the generated UI class
from videoThread import VideoThread  # Import the VideoThread class
from hdbcli import dbapi

class TehseenCode(QDialog):
    def __init__(self):
        super(TehseenCode, self).__init__()
         
        self.ui = UiDialog()  
        self.ui.setup_ui(self)
        
        # Center the window on the screen
        self.center_window()
        
        # Fetch and populate SAP HANA tables
        # self.populate_sap_hana_tables()
    
        # Initialization of variables
        self.logic = 0
        self.value = 1
        self.img_folder = "img" # Folder to save captured images
        os.makedirs(self.img_folder, exist_ok=True)
        self.thread = None
        self.model = None
        self.total_detected_objects = 0
        self.SUMLIST = [] # List to store the count of detected objects
        
        # Detect cameras and populate the dropdown menu with available cameras
        self.detect_cameras()
        
        # Set initial text and UI settings
        self.ui.text_browser.setText('Press "Camera" to connect with camera')
        self.ui.processed_img_label.setScaledContents(True)
        
        # Connect UI buttons to their respective functions
        self.ui.select_excel_btn.clicked.connect(self.upload_excel_file)
        self.ui.upload_img_btn.clicked.connect(self.upload_image)
        self.ui.send_btn.clicked.connect(self.send_data_to_excel)
        self.ui.undo_btn.clicked.connect(self.undo_reset_counter)
        self.ui.reload_btn.clicked.connect(self.reload_app)
        self.ui.quit_btn.clicked.connect(self.quit_app)
        
        self.ui.camera_btn.clicked.connect(self.start_video)
        self.ui.capture_btn.clicked.connect(self.capture_new_image)
        
        # Setup the layout for displaying images
        layout = QHBoxLayout()
        self.ui.frame_right.setLayout(layout)
        layout.addWidget(self.ui.img_label)
        layout.addWidget(self.ui.processed_img_label)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Initialize the YOLO model for object detection
        self.setup_yolo_model()
    
    def center_window(self):
        # Get the screen's geometry
        screen_rect = QDesktopWidget().availableGeometry()
        window_rect = self.frameGeometry()
        
        # Calculate the center position
        x = (screen_rect.width() - window_rect.width()) // 2
        y = (screen_rect.height() - window_rect.height()) // 2
        
        # Move the window to the calculated position
        self.move(x, y)
        
    # Setup the YOLO model with the latest trained weights
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

    # Get the latest modified folder containing the trained model
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
      
    # Start the video stream using the selected camera    
    @pyqtSlot()
    def start_video(self):
        camera_index = self.get_selected_camera_index()
        self.thread = VideoThread(camera_index)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.frame_captured_signal.connect(self.frameCaptured)
        self.thread.camera_failed_signal.connect(self.camera_failed) # Connect to the failure signal
        self.thread.start()

    # Update the image displayed in the UI with the new frame
    @pyqtSlot(QImage)
    def update_image(self, img):
        self.ui.img_label.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot()
    def frameCaptured(self):
        self.ui.text_browser.setText('Image captured')
        
    # Detect connected cameras and populate the dropdown menu
    def detect_cameras(self):
        # Detect connected cameras and populate the dropdown
        camera_indices = []
        # Check the first 5 indices (adjust as needed)
        for i in range(5):  
            cap = cv2.VideoCapture(i)
            
            if cap is not None and cap.isOpened():
                camera_indices.append(i)
                cap.release()
        
        if not camera_indices:
            self.ui.camera_select_combo.addItem("No Cameras Detected")
        else:
            self.ui.camera_select_combo.clear()
            for index in camera_indices:
                self.ui.camera_select_combo.addItem(f"Camera {index}")
        
        self.ui.camera_select_combo.setCurrentIndex(0)
    
    # Get the selected camera index from the dropdown    
    def get_selected_camera_index(self):
        # Stop the video thread
        if self.thread is not None:
            self.thread.stop()
        return self.ui.camera_select_combo.currentIndex()
        
    # Handle the failure of camera initialization
    def camera_failed(self):
        # Handle the camera initialization failure
        QMessageBox.critical(self, "Camera Error", f"Failed to initialize camera with index {self.get_selected_camera_index()}. Please select a different camera.")
        self.ui.text_browser.setText("Failed to start the camera. Please try selecting a different camera.")
        
    # Detect objects in the image and update the UI
    def detect_image(self, image_path):
        output_dir = 'annotated_images'
        os.makedirs(output_dir, exist_ok=True)
        
        # Run the YOLO model on the image
        results = self.model(source=image_path, imgsz=800, conf=0.55, save=False, show_labels=True)
        
        # Debug: Print the total number of objects detected by the model
        num_detected_objects = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
        print(f"Total objects detected by the model: {num_detected_objects}")
        
        detected_image_path = self.draw_bounding_boxes(image_path, results, output_dir)
        
        # Update the total detected objects counter
        # num_detected_objects = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
        self.total_detected_objects += num_detected_objects
        self.SUMLIST.append(num_detected_objects)
        elements = " + ".join(map(str, self.SUMLIST))
        self.ui.text_browser.setText(f'Total: {elements} = {self.total_detected_objects}')
        self.ui.total_objects_label.setText(f'Total Objects: {self.total_detected_objects}')
        return detected_image_path

    # Draw bounding boxes on the detected objects in the image
    def draw_bounding_boxes(self, image_path, results, output_dir):
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Unable to open image file {image_path}")
            return image_path

        height, width, _ = img.shape
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = width / 1500
        font_thickness = 2
        text_color = (0, 0, 255)
        bg_color = (0, 0, 0)
            
        # Extract bounding boxes and sort them
        boxes = [(box.xyxy[0].cpu().numpy().astype(int), idx) for idx, box in enumerate(results[0].boxes)]
        
        # Debug: Print the number of boxes extracted before sorting
        print(f"Total bounding boxes extracted: {len(boxes)}")
        
        row_threshold = height // 100  # This threshold may need to be adjusted

        # First, sort by the y1 coordinate (top of the box)
        boxes.sort(key=lambda b: b[0][1])

        # Then, within each row group, sort by the x1 coordinate (left of the box)
        sorted_boxes = []
        current_row = []
        last_y = boxes[0][0][1]
        for box, idx in boxes:
            if abs(box[1] - last_y) > row_threshold:
                sorted_boxes.extend(sorted(current_row, key=lambda b: b[0][0]))  # Sort by x1 within the row
                current_row = []
                last_y = box[1]
            current_row.append((box, idx))
        sorted_boxes.extend(sorted(current_row, key=lambda b: b[0][0]))  # Sort the last row

        # Debug: Print the number of labels after sorting
        print(f"Total labels after sorting: {len(sorted_boxes)}")
        
        # Draw bounding boxes and labels for each detected object in the correct order
        for new_idx, (box, original_idx) in enumerate(sorted_boxes, start=1):
            x1, y1, x2, y2 = box
            label = f"{new_idx}"
            text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
            text_x = x1 + 5
            text_y = y1 - 10 if y1 - 10 > 0 else y1 + text_size[1] + 10

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (text_x - 5, text_y - text_size[1] - 5),
                          (text_x + text_size[0] + 5, text_y + 5), bg_color, -1)
            cv2.putText(img, label, (text_x, text_y), font, font_scale, text_color, font_thickness)
            
            # Debug: Print the bounding box coordinates and the label
            print(f"Bounding box {new_idx}: x1={x1}, y1={y1}, x2={x2}, y2={y2}, label={label}")

        # Add a title showing the total number of detected objects
        num_boxes = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
        font_scale = width / 800
        font_thickness_title = 4
        title = f"Detected {num_boxes} objects"
        text_size = cv2.getTextSize(title, font, font_scale, font_thickness_title)[0]
        text_x = (width - text_size[0]) - 20
        text_y = text_size[1] + 10
        text_color = (255, 255, 255)
        bg_color = (0, 0, 0)
        cv2.rectangle(img, (text_x - 10, text_y - text_size[1] - 10), 
                      (text_x + text_size[0] + 10, text_y + 10), bg_color, -1)
        cv2.putText(img, title, (text_x, text_y), font, font_scale, text_color, font_thickness)

        # Save the annotated image and update the UI
        output_filename = f'annotated_{os.path.basename(image_path)}'
        output_path = os.path.join(output_dir, output_filename)
        cv2.imwrite(output_path, img)
        
        print(f"Annotated image saved at {output_path}")
        return output_path

    # Convert the frame to QImage format for PyQt display
    def convert_cv_qt(self, cv_img):
        # Convert from BGR to RGB format required by QImage
        rgb_image = cv_img[:,:,::-1].copy()
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w # Calculate the number of bytes per line
        # Convert the image data to QImage format
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # Scale the image to fit the display area while keeping the aspect ratio
        # Get screen resolution
        screen_resolution = QDesktopWidget().screenGeometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()
        
        if screen_width >= 1920 and screen_height >= 1080:
            p = convert_to_qt_format.scaled(790, 610, QtCore.Qt.KeepAspectRatio)
            print("Image Display 790 x 610")
        else:
            p = convert_to_qt_format.scaled(600, 450, QtCore.Qt.KeepAspectRatio)
            print("Image Display 600 x 450")
        return p

    # Open a dialog to select an image for detection
    def upload_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_name:
            # Stop the video thread
            if self.thread is not None:
                self.thread.stop()   
                self.thread = None 
            
            try:
                # Use QTimer.singleShot with a lambda or partial to delay image display
                QTimer.singleShot(100, lambda: self.display_image(file_name, self.ui.img_label))  
            except Exception as e:
                print(f"Fail to display uploaded image: {e}")

            self.detect_image_and_display(file_name)
            
    # Displays the selected image
    def display_image(self, image_path, img_label):
        cv_img = cv2.imread(image_path)
        img_label.setPixmap(QPixmap.fromImage(self.convert_cv_qt(cv_img)))
       
    # Displays the processed image
    def update_processed_image(self, img_path):
        self.display_image(img_path, self.ui.processed_img_label)
            
    # Detects objects, displays the result and send the total_detected_objects to specific excel cell
    def detect_image_and_display(self, image_path):
        detected_image_path = self.detect_image(image_path)
        self.update_processed_image(detected_image_path)  
        
        # Send total_detected_objects to specfic excel cell automation 
        self.send_data_to_excel()
        
        # Send total_detected_objects to selected SAP HANA table
        # self.send_data_to_sap_hana()
        
    # Capture the current frame from the camera and save it as an image
    def capture_new_image(self):
        if self.thread is not None and self.thread.current_frame is not None:
            # Define the path for the image
            img_path = os.path.join(self.img_folder, f"image{self.value}.jpg")
            # Save the current frame
            cv2.imwrite(img_path, self.thread.current_frame)
            self.value += 1
            self.detect_image_and_display(img_path)
        else:
            QMessageBox.critical(self, "Error", "Please connect to a camera to capture")
              
    # Open a dialog to select an Excel file
    def upload_excel_file(self):
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

    # Send the total_detected_objects to the selected cell in Excel
    def send_data_to_excel(self):
        try:
            # Add a small delay to ensure Excel has enough time to register the cell selection
            QTimer.singleShot(100, self.write_data_to_excel)
        except Exception as e:
            print(f"Error writing data to Excel: {e}")
            
    # Writes the total_detected_objects to the given cell in Excel
    def write_data_to_excel(self):
        selected_cell = self.get_selected_cell()
        if selected_cell:
            try:
                self.excel_sheet.range(selected_cell).value = self.total_detected_objects
                self.excel_wb.save()  # Save the changes
            except Exception as e:
                print(f"Error writing data to Excel: {e}")
                self.ui.text_browser.setText('Failed to write data to Excel')
                
    # Get the currently selected cell in the active Excel sheet and update the active sheet reference
    def get_selected_cell(self):
        # Check if the 'excel_wb' attribute exists
        # if not hasattr(self, 'excel_wb') or self.excel_wb is None:
        #     QMessageBox.critical(self, "Error", "Don't have any opened Excel file")
        #     return None
        
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
            # QMessageBox.critical(self, "Error", "Error when getting selected cell") 
        
    # Undo the last operation and update the counter
    def undo_reset_counter(self):
        reply = QMessageBox.question(self, 'Confirm Undo', 'Are you sure you want to undo the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                remove_lastcount = self.SUMLIST.pop()
                SUMLIST = remove_lastcount
                elements = " + ".join(map(str, self.SUMLIST))
                self.total_detected_objects = sum(self.SUMLIST)
                self.ui.text_browser.setText(f'Total Objects: {elements} = {self.total_detected_objects}')
                self.ui.total_objects_label.setText(f'Total Objects: {self.total_detected_objects}')
                self.send_data_to_excel()
            except:
                QMessageBox.critical(self, "Error", "Can Not Undo") 
                print("List empty: Can't Undo")
      
    # Reload the application 
    def reload_app(self):
        reply = QMessageBox.question(self, 'Confirm Reload', 'Are you sure you want to reload the app?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Stop the video thread
            if self.thread is not None:
                self.thread.stop()
            
            # Clear the UI elements if necessary
            self.ui.img_label.clear()
            self.ui.processed_img_label.clear()
            self.ui.text_browser.clear()
            
            # Reinitialize any necessary variables or states
            self.logic = 0
            self.value = 1
            self.thread = None
            self.model = None
            self.total_detected_objects = 0
            self.SUMLIST.clear()
            
            # Reset the camera selection combo box
            self.detect_cameras()
            
            self.ui.text_browser.setText('Press "Camera" to connect with camera')
            self.ui.total_objects_label.setText(f'Total Objects: {self.total_detected_objects}')

            # Reinitialize the YOLO model
            self.setup_yolo_model()
        
    # Quit the application
    def quit_app(self):
        reply = QMessageBox.question(self, 'Confirm Quit', 'Are you sure you want to quit the app?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.thread is not None:
                self.thread.stop()
            QApplication.quit()
            
    ########################################################################
    
    # SAP HANA TRANFER DATA
    # def populate_sap_hana_tables(self):
    #     tables = self.get_sap_hana_tables()
    #     self.ui.table_select_combo.clear()
    #     self.ui.table_select_combo.addItems(tables)
    
    # def connect_to_sap_hana(self):
    #     try:
    #         connection = dbapi.connect(
    #             address="your_hana_host",
    #             port=30015,  # Default SAP HANA port
    #             user="your_username",
    #             password="your_password"
    #         )
    #         print("Connected to SAP HANA")
    #         return connection
    #     except dbapi.Error as e:
    #         print(f"Error connecting to SAP HANA: {e}")
    #         return None
    
    # def get_sap_hana_tables(self):
    #     connection = self.connect_to_sap_hana()
    #     if connection:
    #         try:
    #             cursor = connection.cursor()
    #             cursor.execute("SELECT TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME = 'YOUR_SCHEMA_NAME'")
    #             tables = cursor.fetchall()
    #             return [table[0] for table in tables]  # Return a list of table names
    #         except dbapi.Error as e:
    #             print(f"Error fetching tables: {e}")
    #             return []
    #         finally:
    #             cursor.close()
    #             connection.close()
    #     return []

    # def send_data_to_sap_hana(self):
    #     table_name = self.ui.table_select_combo.currentText()  # Get selected table from combo box
    #     column_name = "YOUR_COLUMN"  # Change this to the correct column name

    #     connection = self.connect_to_sap_hana()
    #     if connection:
    #         try:
    #             cursor = connection.cursor()
    #             query = f"""
    #             INSERT INTO {table_name} ({column_name}, TIMESTAMP)
    #             VALUES (?, CURRENT_TIMESTAMP)
    #             """
    #             cursor.execute(query, (self.total_detected_objects,))
    #             connection.commit()
    #             print(f"Data successfully inserted into {table_name}.")
    #         except dbapi.Error as e:
    #             print(f"Error executing SQL query: {e}")
    #         finally:
    #             cursor.close()
    #             connection.close()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    code = TehseenCode()
    code.show()
    sys.exit(app.exec_())
