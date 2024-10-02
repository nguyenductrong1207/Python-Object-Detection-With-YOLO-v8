import sys
import os
import cv2
from datetime import datetime
from PyQt5 import QtCore, uic, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QHBoxLayout, QMessageBox, QDesktopWidget 
from ultralytics import YOLO
import openpyxl
from openpyxl import load_workbook
import xlwings as xw
from videoThread import VideoThread  # Import the VideoThread class
from hdbcli import dbapi
import numpy as np
from pypylon import pylon
from baslerVideoThread import BaslerVideoThread  # Import the Basler video thread class
import logging

class TehseenCode(QDialog):
    def __init__(self):
        super(TehseenCode, self).__init__()
         
        # Load the UI from the .ui file
        uic.loadUi('ui.ui', self)

        # Set window flags
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        
        # Load and resize the logo image
        logo_pixmap = QtGui.QPixmap("logo.webp") 
        logo_pixmap = logo_pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo_icon = QtGui.QIcon(logo_pixmap)
        self.setWindowIcon(logo_icon)
        
        # Center the window on the screen
        self.center_window()
    
        # Initialization of variables
        self.logic = 0
        self.value = 1
        self.img_folder = "img" # Folder to save captured images
        os.makedirs(self.img_folder, exist_ok=True)
        self.thread = None
        self.model = None
        self.total_detected_objects = 0
        self.SUMLIST = [] # List to store the count of detected objects
        
        # Initialize basler camera attributes
        self.basler_video_thread = None
        self.basler_camera = None
        self.is_basler_camera = False
        
        # Detect cameras and populate the dropdown menu with available cameras
        self.detect_cameras()
        
        # Set initial text and UI settings
        self.textBrowser.setText('Press "Camera" to connect with camera')
        self.processedImgLabel.setScaledContents(True)
        
        # Connect UI buttons to their respective functions
        self.selectExcelBtn.clicked.connect(self.upload_excel_file)
        self.uploadImgBtn.clicked.connect(self.upload_image)
        self.sendBtn.clicked.connect(self.send_data_to_excel)
        self.undoBtn.clicked.connect(self.undo_reset_counter)
        self.reloadBtn.clicked.connect(self.reload_app)
        self.quitBtn.clicked.connect(self.quit_app)
        
        self.cameraBtn.clicked.connect(self.start_camera)
        
        self.captureBtn.clicked.connect(self.capture_new_image)
        self.detectLastestImgBtn.clicked.connect(self.detect_latest_image)
        
        self.baslerCameraBtn.clicked.connect(self.capture_from_basler_camera)
        
        # Setup the layout for displaying images
        layout = QHBoxLayout()
        self.frameRight.setLayout(layout)
        layout.addWidget(self.imgLabel)
        layout.addWidget(self.processedImgLabel)
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
    def start_video(self, camera_index):
        # camera_index = self.get_selected_camera_index()
        
        # Stop the current video thread if it's running
        if self.thread is not None:
            self.thread.stop()
        
        # Initialize the video thread with the selected camera index
        self.thread = VideoThread(camera_index)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.frame_captured_signal.connect(self.frameCaptured)
        self.thread.camera_failed_signal.connect(self.camera_failed) # Connect to the failure signal
        self.thread.start()

    # Update the image displayed in the UI with the new frame
    @pyqtSlot(QImage)
    def update_image(self, img):
        self.imgLabel.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot()
    def frameCaptured(self):
        self.textBrowser.setText('Image captured')
        
    def stop_all_cameras(self):
        # Stop the regular webcam thread
        if self.thread is not None:
            if self.thread.isRunning():
                self.thread.stop()
                self.thread.wait()  # Ensure the thread is completely stopped
            self.thread = None

        # Stop the Basler camera thread
        if self.basler_video_thread is not None:
            if self.basler_video_thread.isRunning():
                self.basler_video_thread.stop()
                self.basler_video_thread.wait()  # Ensure the thread is completely stopped
            self.basler_video_thread = None

        # Close the Basler camera if it is open
        if self.basler_camera is not None:
            if self.basler_camera.IsOpen():
                self.basler_camera.StopGrabbing()  # Ensure grabbing is stopped
                self.basler_camera.Close()  # Close the camera
            self.basler_camera = None
    
    # Start the Basler Camera using the selected camera     
    def start_camera(self):
        selected_camera = self.cameraSelectCombo.currentText()
        
        logging.info(f"Switching to camera: {selected_camera}")
        
        try:
            # Stop all currently running cameras (both Basler and regular)
            self.stop_all_cameras()

            if selected_camera == "Basler Camera":
                self.is_basler_camera = True
                self.connect_basler_camera()  # Start Basler camera
            else:
                # Handle the regular webcam
                self.is_basler_camera = False
                
                # Calculate the camera index (subtract 1 because Basler is first option)
                camera_index = self.cameraSelectCombo.currentIndex() - 1
                if camera_index >= 0:
                    self.start_video(camera_index)  # Start the webcam stream
        except Exception as e:
            logging.error(f"Error starting camera: {str(e)}")
            QMessageBox.critical(self, "Camera Error", f"Failed to switch camera: {str(e)}")
    
    # Connect to the Basler camera with camera IP       
    def connect_basler_camera(self):
        try:
            # Connect to the Basler camera
            self.basler_camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(pylon.DeviceInfo().SetIpAddress("192.168.3.3")))
            
            if not self.basler_camera.IsOpen():
                self.basler_camera.Open()

            # Ensure the camera is not already grabbing
            if self.basler_camera.IsGrabbing():
                self.basler_camera.StopGrabbing()

            # Set camera settings
            max_width = self.basler_camera.Width.GetMax()
            max_height = self.basler_camera.Height.GetMax()
            self.basler_camera.Width.SetValue(max_width)
            self.basler_camera.Height.SetValue(max_height)
            self.basler_camera.Gain.SetValue(10)
            self.basler_camera.ExposureTime.SetValue(5000)
            
            # Start the Basler video thread to display the video feed in real-time
            self.basler_video_thread = BaslerVideoThread(self.basler_camera)
            self.basler_video_thread.change_pixmap_signal.connect(self.update_image)
            self.basler_video_thread.start()
            
        except pylon.GenericException as e:
            # Catch any errors specifically related to Basler camera API
            QMessageBox.critical(self, "Basler Camera Error", f"Failed to connect to Basler Camera: {str(e)}")

        except Exception as e:
            QMessageBox.critical(self, "Basler Camera Error", f"Failed to connect to Basler Camera: {str(e)}")
            
    # Handle the Basler camera capture    
    def capture_from_basler_camera(self):
        if self.is_basler_camera and self.basler_camera is not None:
            try:
                # if self.basler_camera.IsGrabbing():
                #     self.basler_camera.StopGrabbing()  # Stop the camera if it's currently grabbing
                
                # Capture the image from the Basler camera
                grab_result = self.basler_camera.GrabOne(25000)
                if grab_result.GrabSucceeded():
                    image = grab_result.Array

                    # Define the path for the image
                    img_path = os.path.join(self.img_folder, f"basler_image{self.value}.png")
                
                    # Save the image captured from Basler camera
                    cv2.imwrite(img_path, image)
                    self.value += 1  # Increment image counter

                    # Now that the image is saved, detect and display the image
                    self.detect_image_and_display(img_path)  # Detect objects and display the image

                else:
                    QMessageBox.critical(self, "Capture Failed", "Failed to capture image from Basler camera.")

            except Exception as e:
                QMessageBox.critical(self, "Camera Error", f"Error capturing image from Basler camera: {str(e)}")
                print(e)

        else:
            QMessageBox.warning(self, "Camera Not Connected", "Basler Camera is not connected. Please connect it first.")   
    
    # Detect connected cameras and populate the dropdown menu
    def detect_cameras(self):
        # Add Basler Camera as the first option in cameraSelectCombo
        self.cameraSelectCombo.addItem("Basler Camera")
        
        # Detect regular cameras and add them to the combo box
        for i in range(5):  
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cameraSelectCombo.addItem(f"Camera {i}")
                cap.release()

        self.cameraSelectCombo.setCurrentIndex(0)
        
        # # Detect connected cameras and populate the dropdown
        # camera_indices = []
        
        # # Check the first 4 indices (adjust as needed)
        # for i in range(4):  
        #     cap = cv2.VideoCapture(i)
            
        #     if cap is not None and cap.isOpened():
        #         camera_indices.append(i)
        #         cap.release()
        
        # if not camera_indices:
        #     self.cameraSelectCombo.addItem("No Cameras Detected")
        # else:
        #     self.cameraSelectCombo.clear()
            
        #     # Add Basler Camera as the first option in cameraSelectCombo
        #     self.cameraSelectCombo.addItem("Basler Camera")
            
        #     for index in camera_indices:
        #         self.cameraSelectCombo.addItem(f"Camera {index}")
        
        # self.cameraSelectCombo.setCurrentIndex(0)
    
    # Get the selected camera index from the dropdown    
    def get_selected_camera_index(self):
        # Stop the video thread
        if self.thread is not None:
            self.thread.stop()
        return self.cameraSelectCombo.currentIndex()
        
    # Handle the failure of camera initialization
    def camera_failed(self):
        # Handle the camera initialization failure
        QMessageBox.critical(self, "Camera Error", f"Failed to initialize camera with index {self.get_selected_camera_index()}. Please select a different camera.")
        self.textBrowser.setText("Failed to start the camera. Please try selecting a different camera.")
        
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
        # self.total_detected_objects += num_detected_objects
        # self.SUMLIST.append(num_detected_objects)
        elements = " + ".join(map(str, self.SUMLIST))
        self.textBrowser.setText(f'Total: {elements} = {self.total_detected_objects}')
        self.totalObjectsLabel.setText(f'Total Objects: {self.total_detected_objects}')
        
        return detected_image_path

    # # Draw bounding boxes on the detected objects in the image
    # def draw_bounding_boxes(self, image_path, results, output_dir):
    #     img = cv2.imread(image_path)
    #     if img is None:
    #         print(f"Error: Unable to open image file {image_path}")
    #         return image_path

    #     height, width, _ = img.shape
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     font_scale = width / 1500
    #     font_thickness = 2
    #     text_color = (0, 0, 255)
    #     bg_color = (0, 0, 0)
            
    #     # Extract bounding boxes and sort them
    #     boxes = [(box.xyxy[0].cpu().numpy().astype(int), idx) for idx, box in enumerate(results[0].boxes)]
        
    #     # Debug: Print the number of boxes extracted before sorting
    #     print(f"Total bounding boxes extracted: {len(boxes)}")
        
    #     # Check if boxes list is empty
    #     if not boxes:  
    #         QMessageBox.information(self, "No Objects Detected", "No objects were detected in the image.", QMessageBox.Ok)
    #         return image_path
        
    #     row_threshold = height // 100  # This threshold may need to be adjusted

    #     # First, sort by the y1 coordinate (top of the box)
    #     boxes.sort(key=lambda b: b[0][1])

    #     # Then, within each row group, sort by the x1 coordinate (left of the box)
    #     sorted_boxes = []
    #     current_row = []
    #     last_y = boxes[0][0][1]
    #     for box, idx in boxes:
    #         if abs(box[1] - last_y) > row_threshold:
    #             sorted_boxes.extend(sorted(current_row, key=lambda b: b[0][0]))  # Sort by x1 within the row
    #             current_row = []
    #             last_y = box[1]
    #         current_row.append((box, idx))
    #     sorted_boxes.extend(sorted(current_row, key=lambda b: b[0][0]))  # Sort the last row

    #     # Debug: Print the number of labels after sorting
    #     print(f"Total labels after sorting: {len(sorted_boxes)}")
        
    #     # Draw bounding boxes and labels for each detected object in the correct order
    #     for new_idx, (box, original_idx) in enumerate(sorted_boxes, start=1):
    #         x1, y1, x2, y2 = box
    #         label = f"{new_idx}"
    #         text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
    #         text_x = x1 + 5
    #         text_y = y1 - 10 if y1 - 10 > 0 else y1 + text_size[1] + 10

    #         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #         cv2.rectangle(img, (text_x - 5, text_y - text_size[1] - 5),
    #                       (text_x + text_size[0] + 5, text_y + 5), bg_color, -1)
    #         cv2.putText(img, label, (text_x, text_y), font, font_scale, text_color, font_thickness)
            
    #         # Debug: Print the bounding box coordinates and the label
    #         print(f"Bounding box {new_idx}: x1={x1}, y1={y1}, x2={x2}, y2={y2}, label={label}")

    #     # Add a title showing the total number of detected objects
    #     num_boxes = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
    #     font_scale = width / 800
    #     font_thickness_title = 4
    #     title = f"Detected {num_boxes} objects"
    #     text_size = cv2.getTextSize(title, font, font_scale, font_thickness_title)[0]
    #     text_x = (width - text_size[0]) - 20
    #     text_y = text_size[1] + 10
    #     text_color = (255, 255, 255)
    #     bg_color = (0, 0, 0)
    #     cv2.rectangle(img, (text_x - 10, text_y - text_size[1] - 10), 
    #                   (text_x + text_size[0] + 10, text_y + 10), bg_color, -1)
    #     cv2.putText(img, title, (text_x, text_y), font, font_scale, text_color, font_thickness)

    #     # Save the annotated image and update the UI
    #     output_filename = f'annotated_{os.path.basename(image_path)}'
    #     output_path = os.path.join(output_dir, output_filename)
    #     cv2.imwrite(output_path, img)
        
    #     print(f"Annotated image saved at {output_path}")
    #     return output_path
    
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
            
        # Extract bounding boxes and associated labels
        boxes = [(box.xyxy[0].cpu().numpy().astype(int), idx) for idx, box in enumerate(results[0].boxes)]
        
        # Debug: Print the number of boxes extracted before sorting
        print(f"Total bounding boxes extracted: {len(boxes)}")
        
        if not boxes:  # Check if boxes list is empty
            QMessageBox.information(self, "No Objects Detected", "No objects were detected in the image.", QMessageBox.Ok)
            return image_path

        # Check for and remove duplicate bounding boxes
        unique_boxes = []
        for box, idx in boxes:
            is_duplicate = False
            for unique_box, _ in unique_boxes:
                # Simple duplication check: same coordinates or very close (adjust threshold as needed)
                if np.allclose(box, unique_box, atol=5):  
                    is_duplicate = True
                    print(f"Duplicate bounding box found at index {idx} with coordinates {box}")
                    break
            if not is_duplicate:
                unique_boxes.append((box, idx))
        
        # Debug: Print the number of unique boxes after filtering duplicates
        print(f"Total unique bounding boxes: {len(unique_boxes)}")
        
        # Sorting bounding boxes
        row_threshold = height // 100  # Adjust this threshold as needed
        unique_boxes.sort(key=lambda b: b[0][1])  # Sort by y1

        sorted_boxes = []
        current_row = []
        last_y = unique_boxes[0][0][1]
        for box, idx in unique_boxes:
            if abs(box[1] - last_y) > row_threshold:
                sorted_boxes.extend(sorted(current_row, key=lambda b: b[0][0]))  # Sort by x1 within the row
                current_row = []
                last_y = box[1]
            current_row.append((box, idx))
        sorted_boxes.extend(sorted(current_row, key=lambda b: b[0][0]))  # Sort the last row

        # Debug: Print the sorted bounding boxes with their new labels
        print("Sorted bounding boxes and their new labels:")
        for new_idx, (box, original_idx) in enumerate(sorted_boxes, start=1):
            print(f"Original Index: {original_idx}, New Label: {new_idx}, Coordinates: {box}")
            
            # Drawing the bounding box and label on the image
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

        # Update total detected objects with the count of unique bounding boxes
        self.total_detected_objects += len(unique_boxes)
        self.SUMLIST.append(len(unique_boxes))
        
        # Add a title showing the total number of detected objects
        # num_boxes = results[0].boxes.shape[0] if len(results[0].boxes.shape) > 0 else 0
        font_scale = width / 800
        font_thickness_title = 4
        title = f"Detected {len(unique_boxes)} objects"
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
                QTimer.singleShot(100, lambda: self.display_image(file_name, self.imgLabel))  
            except Exception as e:
                print(f"Fail to display uploaded image: {e}")

            self.detect_image_and_display(file_name)
            
    # Displays the selected image
    def display_image(self, image_path, img_label):
        cv_img = cv2.imread(image_path)
        img_label.setPixmap(QPixmap.fromImage(self.convert_cv_qt(cv_img)))
       
    # Displays the processed image
    def update_processed_image(self, img_path):
        self.display_image(img_path, self.processedImgLabel)
            
    # Detects objects, displays the result and send the total_detected_objects to specific excel cell
    def detect_image_and_display(self, image_path):
        detected_image_path = self.detect_image(image_path)
        
        # Send total_detected_objects to specfic excel cell automation 
        self.send_data_to_excel()
        
        self.update_processed_image(detected_image_path)  
        
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
            
    def detect_latest_image(self):
        # Change the img folder link with your PC link
        img_folder = r"D:\Github\Python-Object-Detection-With-YOLO-v8\ObjectDetection\ObjectDectecionWithOpenCV\img"

        try:
            # Get the list of all files in the img folder
            images = [os.path.join(self.img_folder, f) for f in os.listdir(img_folder) if os.path.isfile(os.path.join(img_folder, f))]
            
            if not images:
                # Show a message box if no images are found in the folder
                QMessageBox.warning(self, "No Images", "No images found in the 'img' folder.")
                return

            # Stop the video thread
            if self.thread is not None:
                self.thread.stop()   
                self.thread = None 
                
            # Find the latest image by modification time
            latest_image = max(images, key=os.path.getmtime)
            
            try:
                # Use QTimer.singleShot with a lambda or partial to delay image display
                QTimer.singleShot(100, lambda: self.display_image(latest_image, self.imgLabel))  
            except Exception as e:
                print(f"Fail to display latest image: {e}")
         
            # Display and process the latest image
            self.detect_image_and_display(latest_image)
            
            # Extract and print the image name
            image_name = os.path.basename(latest_image)
            print(f"Latest image detected: {image_name}")

        except Exception as e:
            print(f"Error detecting the latest image: {e}")
            QMessageBox.critical(self, "Error", f"Failed to detect the latest image: {str(e)}")  
              
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
            QTimer.singleShot(300, self.write_data_to_excel)
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
                self.textBrowser.setText('Failed to write data to Excel')
                
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
                removed_count  = self.SUMLIST.pop()
                self.total_detected_objects -= removed_count
                
                elements = " + ".join(map(str, self.SUMLIST))
                # self.total_detected_objects = sum(self.SUMLIST)
                self.textBrowser.setText(f'Total Objects: {elements} = {self.total_detected_objects}')
                self.totalObjectsLabel.setText(f'Total Objects: {self.total_detected_objects}')
                
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
            self.imgLabel.clear()
            self.processedImgLabel.clear()
            self.textBrowser.clear()
            
            # Reinitialize any necessary variables or states
            self.logic = 0
            self.value = 1
            self.thread = None
            self.model = None
            self.total_detected_objects = 0
            self.SUMLIST.clear()
            
            # Reset the camera selection combo box
            self.detect_cameras()
            
            self.textBrowser.setText('Press "Camera" to connect with camera')
            self.totalObjectsLabel.setText(f'Total Objects: {self.total_detected_objects}')

            # Reinitialize the YOLO model
            self.setup_yolo_model()
        
    # Quit the application
    def quit_app(self):
        reply = QMessageBox.question(self, 'Confirm Quit', 'Are you sure you want to quit the app?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Stop all running cameras (both webcam and Basler)
            self.stop_all_cameras()
            
            if self.thread is not None:
                self.thread.stop()
            QApplication.quit()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    code = TehseenCode()
    code.show()
    sys.exit(app.exec_())
