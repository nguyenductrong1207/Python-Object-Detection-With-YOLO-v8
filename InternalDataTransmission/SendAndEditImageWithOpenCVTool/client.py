import sys
import io
import socket
import threading
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, 
    QSplitter, QMessageBox, QPushButton, QDialog, QFormLayout, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage, QDrag, QPainter, QPen, QFont
from PyQt5.QtCore import QBuffer, QByteArray, Qt, QMimeData
import base64

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()  
        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)  
        self.server_thread.start()
        # Stack to store image versions
        self.image_stack = [] 

    def init_ui(self):
        self.setWindowTitle("Client View")  
        self.setFixedSize(1400, 600)  

        central_widget = QWidget()  # Create the central widget
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)  # Set a horizontal layout for the central widget ( by default )

        splitter = QSplitter()  # Create a splitter to divide the UI into 2 parts
        layout.addWidget(splitter)
        
        #########################################################################################
        
        # Create a widget for the left part
        left_widget = QWidget()  
        left_widget.setFixedWidth(700)  
        
        # Set a layout for the left widget
        left_layout = QVBoxLayout(left_widget)  
        
        # Add the left widget to the splitter
        splitter.addWidget(left_widget)  

        #########################################################################################
        
        # Create a layout for the file path 
        self.file_layout = QHBoxLayout()  
        self.file_label = QLabel("Excel file path:") 
        self.file_edit = QLineEdit()  
        
        self.file_edit.setReadOnly(True)
        self.file_edit.setFixedHeight(35)  
        
        # Add the file label, file edit to the file layout
        self.file_layout.addWidget(self.file_label) 
        self.file_layout.addWidget(self.file_edit)  
        
        # Add the file layout to the left layout
        left_layout.addLayout(self.file_layout)  
        
        #########################################################################################

        # Create a layout for the sheet name and money amount
        self.sheet_layout = QHBoxLayout()  
        self.sheet_label = QLabel("Sheet name:") 
        self.sheet_combo = QComboBox() 
        
        self.sheet_combo.setEnabled(False) 
        self.sheet_combo.setFixedWidth(240) 
        self.sheet_combo.setFixedHeight(35) 
        
        # Add the sheet label, sheet combobox to the layout
        self.sheet_layout.addWidget(self.sheet_label)  
        self.sheet_layout.addWidget(self.sheet_combo)  
        
        # Add the sheet layout to the left layout
        left_layout.addLayout(self.sheet_layout)  
        
        #########################################################################################

         # Create a received data label and add to the left layout
        self.label = QLabel("Received Data:") 
        left_layout.addWidget(self.label)  
        
        #########################################################################################

        # Create a table widget for displaying the results and add to the left layout
        self.result_table = QTableWidget()  
        left_layout.addWidget(self.result_table) 
        
        #########################################################################################

        # Create a widget for the right part - Image Display
        right_widget = QWidget() 
        right_widget.setFixedWidth(700)  
        
        # Set a layout for the right widget
        right_layout = QVBoxLayout(right_widget)  
        
        # Add the right widget to the splitter
        splitter.addWidget(right_widget)  
        
        #########################################################################################

        # Create a layout for the image buttons
        buttons_layout = QHBoxLayout()  

        # Create send button and add to the buttons layout
        self.edit_button = QPushButton("Edit Image")
        self.edit_button.clicked.connect(self.edit_image)  
        self.edit_button.setFixedHeight(35)  
        self.edit_button.setVisible(False)
        buttons_layout.addWidget(self.edit_button) 
        
        # Create go back button and add to the buttons layout
        self.go_back_button = QPushButton("Go Back")
        self.go_back_button.clicked.connect(self.go_back_change)
        self.go_back_button.setFixedHeight(35)  
        self.go_back_button.setVisible(False)
        buttons_layout.addWidget(self.go_back_button) 
        
        # Create downkoad button and add to the buttons layout
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_image)  
        self.download_button.setFixedHeight(35)  
        self.download_button.setVisible(False)
        buttons_layout.addWidget(self.download_button) 
         
        # Create send button and add to the buttons layout
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_image)  
        self.send_button.setFixedHeight(35)  
        self.send_button.setVisible(False)
        buttons_layout.addWidget(self.send_button) 
                 
        # Add the buttons layout to the right layout
        right_layout.addLayout(buttons_layout) 
        
        #########################################################################################
       
        # Create label for image and add to the right layout
        self.image_label_title = QLabel("") 
        right_layout.addWidget(self.image_label_title)
        
        # Create label to display the image and add to the right layout
        self.image_label = QLabel("No image received")  
        right_layout.addWidget(self.image_label) 

        #########################################################################################
        
        # Show the main window
        self.show()  
    
    #############################################################################################
    
    # Function for continuously listens for incoming connections, receives data from connected server, 
    # and processes the data to either display it as JSON in a table or as an image
    def start_server(self):
        # Replace with the server's IP address
        server_ip = '127.0.0.1'  
        server_port = 12345  
        
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        # Bind the socket to the address and port
        server_socket.bind((server_ip, server_port))  
        # Listen for incoming connections
        server_socket.listen(1)  

        while True:
            try:
                # Accepting Connections and Receiving Data
                # Accept a new connection
                client_socket, _ = server_socket.accept()  
                data = b''
                while True:
                    # Receive data in chunks
                    part = client_socket.recv(1024)  
                    if not part:
                        break
                    data += part
                
                # Processing the Received Data    
                # Check if the data is JSON
                if data.startswith(b'{'):  
                    # Display the JSON data
                    self.display_data(data)  
                else:
                    # Display the image data
                    self.display_image(data)  
                # Close the client socket
                client_socket.close()  
                
            except Exception as e:
                QMessageBox.critical(self, "Error in Server: ", str(e)) 

    #############################################################################################
    
    # Function for Displaying the Getting Data
    def display_data(self, data):
        try:
            # Decode and load the JSON data
            data = json.loads(data.decode('utf-8'))  
            # Set the file path in the line edit
            self.file_edit.setText(data['file_path'])  
            
            # Clear, Add the sheet name to the combo box and Set the current text of the combo box
            self.sheet_combo.clear()  
            self.sheet_combo.addItem(data['sheet_name'])   
            self.sheet_combo.setCurrentText(data['sheet_name']) 

            # Clear previous data in the table before display new data
            self.result_table.setRowCount(0)  
            
            # Set the number of columns in the table
            self.result_table.setColumnCount(4)  
            # Set the column headers
            self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name"])  

            # Iterate through the results
            for result in data['results']:  
                # Get the current number of rows in the table
                row_position = self.result_table.rowCount()  
                # Insert a new row
                self.result_table.insertRow(row_position)  
                
                # Set the money amount, time repeated, total amount and current sheet name to the table
                self.result_table.setItem(row_position, 0, QTableWidgetItem(result['money']))  
                self.result_table.setItem(row_position, 1, QTableWidgetItem(result['time_repeated']))  
                self.result_table.setItem(row_position, 2, QTableWidgetItem(result['total']))
                self.result_table.setItem(row_position, 3, QTableWidgetItem(result['sheet_name']))  

            # Make the table read-only
            self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)  
            
        except Exception as e:
            QMessageBox.critical(self, "Error displaying data: ", str(e)) 

    #############################################################################################
    
    # Function for Displaying the Getting Image
    def display_image(self, data):
        try:
            # Save current image version to stack if an image is already loaded
            if self.image_label.pixmap() is not None:
                current_image = self.image_label.pixmap().toImage()
                current_width = self.image_label.pixmap().width()
                current_height = self.image_label.pixmap().height()
                
                # Append current image and its dimensions to the stack
                self.image_stack.append({
                    'image': current_image,
                    'width': current_width,
                    'height': current_height
                })
            
            # Open a file to write the image data
            with open("received_image.png", "wb") as file:  
                # Write the image data to the file
                file.write(data)  
            # Load and scale the image
            # pixmap = QPixmap("received_image.png").scaled(600, 600, aspectRatioMode=1)  
            pixmap = QPixmap("received_image.png")
            # Display the image in the label
            self.image_label.setPixmap(pixmap)  
            # Clear the text "No image selected" in the label
            self.image_label.setText("") 
            # Set text for the image_label_title label
            self.image_label_title.setText("Image Sent")
            # Set Visible for Edit Image and Send Button
            self.edit_button.setVisible(True)
            self.send_button.setVisible(True)
            self.go_back_button.setVisible(True)
            self.download_button.setVisible(True)    
            
        except Exception as e:
            QMessageBox.critical(self, "Error displaying image: ", str(e)) 
         
    #############################################################################################
    
    # Function for Editing the Getting Image
    def edit_image(self):
        dialog = EditImageDialog(self)
        
        current_image = self.image_label.pixmap().toImage()
        current_width = self.image_label.pixmap().width()
        current_height = self.image_label.pixmap().height()
            
        dialog.height_edit.setText(str(current_height))
        dialog.width_edit.setText(str(current_width))
        
        if dialog.convert_button.clicked:
            dialog.convert_button.clicked.connect(self.convert_to_grayscale)
            
        # If the dialog is accepted (OK button clicked)
        if dialog.exec_() == QDialog.Accepted:
            height = int(dialog.height_edit.text())
            width = int(dialog.width_edit.text())
            text = dialog.text_edit.text()
            
            if height > 0 and width > 0 and self.image_label.pixmap() is not None: 
                # Save the current image to the stack before editing
                self.image_stack.append({
                    'image': current_image,
                    'width': current_width,
                    'height': current_height
                })
                
                # Scale the image to the new dimensions and display it
                pixmap = self.image_label.pixmap().scaled(width, height)
                self.image_label.setPixmap(pixmap)
                
                if text:
                    draggable_label = DraggableLabel(text, self.image_label)
                    draggable_label.move(50, 50)  # Initial position
                    draggable_label.show()
                    self.draggable_label = draggable_label  # Save reference to draggable
                
            else:
                QMessageBox.warning(self, "Input Error", "Please enter valid height and width to resize Image")
    
    #############################################################################################
    
    # Function to convert the image to grayscale            
    def convert_to_grayscale(self):
        pixmap = self.image_label.pixmap()
        if pixmap is not None:
            current_image = pixmap.toImage()
            current_width = pixmap.width()
            current_height = pixmap.height()
            
            # Save the current image to the stack before converting
            self.image_stack.append({
                'image': current_image,
                'width': current_width,
                'height': current_height
            })
            
            # Convert QPixmap to QImage    
            qimage = pixmap.toImage()
            # Convert QImage to OpenCV image
            cv_image = self.qimage_to_cvimage(qimage)
            # Convert the image to grayscale
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            # Get the dimensions of the grayscale image
            height, width = gray_image.shape
            
            # Convert the grayscale image back to QImage
            qimage = QImage(gray_image.data, width, height, gray_image.strides[0], QImage.Format.Format_Grayscale8)
            # Display the grayscale image
            self.image_label.setPixmap(QPixmap.fromImage(qimage))
    
    #############################################################################################
    
    # Function to convert QImage to OpenCV image
    def qimage_to_cvimage(self, qimage):
        # Convert QImage to RGBA format
        qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()
        
        # Get the image data
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        # Convert the data to a NumPy array
        arr = np.array(ptr).reshape((height, width, 4))
        # Return the RGB channels of the image
        return arr[:, :, :3]  
    
    def add_text_to_image(self, text):
        if self.image_label.pixmap() is not None and text:
            pixmap = self.image_label.pixmap()
            image = pixmap.toImage()
            
            # Convert QImage to QPixmap
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red))
            painter.setFont(QFont("Arial", 20))
            painter.drawText(image.rect(), Qt.AlignCenter, text)
            painter.end()
            
            # Place text at a fixed position (can be enhanced to allow drag and drop)
            # painter.drawText(50, 50, text)
            # painter.end()
            
            # self.image_label.setPixmap(pixmap)
            self.image_label.setPixmap(QPixmap.fromImage(image))
            self.image_label.setAlignment(Qt.AlignCenter)
    
    # Method to update the image with text
    def update_image_with_text(self, text, pos):
        if self.image_label.pixmap() is not None:
            pixmap = self.image_label.pixmap()
            image = pixmap.toImage()

            # Convert QImage to QPixmap for QPainter
            painter = QPainter()
            painter.begin(image)
            painter.setPen(QPen(Qt.red))  # Set text color
            painter.setFont(QFont('Arial', 20))  # Set text font and size
            painter.drawText(pos, text)  # Draw text at the specified position
            painter.end()

            self.image_label.setPixmap(QPixmap.fromImage(image))
        
    #############################################################################################
    
    # Function to go back to the previous image version      
    def go_back_change(self):
        if self.image_stack:
            # Get the last image version from the stack
            previous_version = self.image_stack.pop()
            previous_image = previous_version['image']
            previous_width = previous_version['width']
            previous_height = previous_version['height']
            
            # Scale the previous image to its original dimensions and display it
            pixmap = QPixmap.fromImage(previous_image).scaled(previous_width, previous_height, aspectRatioMode=1)
            self.image_label.setPixmap(pixmap)
        else:
            QMessageBox.warning(self, "No Previous Image", "No previous image to go back")

    def download_image(self):
        if self.image_label.pixmap() is not None:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)", options=options)
            
            if file_path:
                try:
                    qimage = self.image_label.pixmap().toImage()
                    painter = QPainter(qimage)
                    
                    for child in self.image_label.children():
                        if isinstance(child, DraggableLabel):
                            pos = child.pos()
                            painter.drawText(pos, child.text())
                    
                    painter.end()
                    qimage.save(file_path, "PNG")
                    QMessageBox.information(self, "Success", "Image downloaded successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to download image: {str(e)}")
        else:
            QMessageBox.warning(self, "No Image", "No image to download.")
    
    #############################################################################################
    # Function for Sending Back the Editting Image
    def send_image(self):
        if self.image_label.pixmap() is not None:
            # Convert the QPixmap to QImage
            qimage = self.image_label.pixmap().toImage()
            
            # Convert the QImage to byte array
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            qimage.save(buffer, "PNG")
            byte_array = buffer.data()
            
            # Encode byte array in base64 to handle binary data in JSON
            encoded_image = base64.b64encode(byte_array).decode('utf-8')

            # Gather all text items from draggable labels
            text_data = []
            for widget in self.image_label.findChildren(DraggableLabel):
                text_data.append({
                    'text': widget.text(),
                    'x': widget.x(),
                    'y': widget.y()
                })

            # Create a JSON object with image and text data
            payload = {
                'image': encoded_image,
                'texts': text_data
            }

            # Serialize the JSON object
            json_payload = json.dumps(payload).encode('utf-8')
            
            # Send the byte array to the server
            try:
                # Replace with the server's IP address and port
                server_ip = '127.0.0.1'
                server_port = 54321
                
                # Create a TCP/IP socket
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect to the server
                client_socket.connect((server_ip, server_port))
                # Send the image data
                client_socket.sendall(json_payload)
                # Close the socket
                client_socket.close()
                
                QMessageBox.information(self, "Success", "Image sent back to server successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error sending image: ", str(e))
        else:
            QMessageBox.warning(self, "No Image", "No image to send back.")
    
#################################################################################################

class EditImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Image")
        self.setFixedSize(600, 300)

        main_layout = QHBoxLayout(self) 
        
        left_widget = QWidget()
        left_widget.setFixedWidth(300)
        left_layout = QVBoxLayout(left_widget)

        # Create a label and text field for height and add to the form layout
        height_layout = QHBoxLayout()  
        self.height_label = QLabel("Height:", self)
        self.height_edit = QLineEdit(self)
        self.height_edit.setFixedHeight(35)
        height_layout.addWidget(self.height_label)
        height_layout.addWidget(self.height_edit)
        left_layout.addLayout(height_layout)

        # Create a label and text field for width and add to the form layout
        width_layout = QHBoxLayout() 
        self.width_label = QLabel("Width:", self)
        self.width_edit = QLineEdit(self)
        self.width_edit.setFixedHeight(35)
        width_layout.addWidget(self.width_label)
        width_layout.addWidget(self.width_edit)
        left_layout.addLayout(width_layout)
        
        # Create a convert button and add to the form layout
        self.convert_button = QPushButton("Convert To Grayscale")
        self.convert_button.setFixedHeight(35)
        left_layout.addWidget(self.convert_button)

        # Create an OK button, connect it to the accept method, and add to the form layout
        self.ok_button = QPushButton("OK", self)
        self.ok_button.setFixedHeight(35)
        self.ok_button.clicked.connect(self.accept)
        left_layout.addWidget(self.ok_button)

        main_layout.addWidget(left_widget)
        
        ####
        # Right side (new UI for text option)
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_layout = QVBoxLayout(right_widget)

        self.text_option_label = QLabel("Text Option:", self)
        self.text_edit = QLineEdit(self)
        self.text_edit.setFixedHeight(35)

        right_layout.addWidget(self.text_option_label)
        right_layout.addWidget(self.text_edit)

        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont('Arial', 20))
        self.setStyleSheet("color: red;")  
        self.setFixedSize(self.sizeHint())  # Size to fit the text
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            
#################################################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)  
    client_app = ClientApp()  # Create an instance of the main window
    sys.exit(app.exec_())  # Start the event loop
