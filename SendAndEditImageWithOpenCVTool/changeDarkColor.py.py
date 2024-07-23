import sys
import socket
import threading
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSplitter, QMessageBox, QPushButton, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QBuffer

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui() 
        self.image_path = None
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)  
        self.server_thread.start()

    def init_ui(self):
        self.setWindowTitle("Client View")  
        self.setFixedSize(1400, 600)  

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        splitter = QSplitter()
        layout.addWidget(splitter)
        
        left_widget = QWidget()  
        left_widget.setFixedWidth(700)  
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)

        self.file_layout = QHBoxLayout()  
        self.file_label = QLabel("Excel file path:") 
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        self.file_edit.setFixedHeight(35)  
        self.file_layout.addWidget(self.file_label)
        self.file_layout.addWidget(self.file_edit)
        left_layout.addLayout(self.file_layout)  

        self.sheet_layout = QHBoxLayout()  
        self.sheet_label = QLabel("Sheet name:") 
        self.sheet_combo = QComboBox()
        self.sheet_combo.setEnabled(False) 
        self.sheet_combo.setFixedWidth(240) 
        self.sheet_combo.setFixedHeight(35) 
        self.sheet_layout.addWidget(self.sheet_label)  
        self.sheet_layout.addWidget(self.sheet_combo)  
        left_layout.addLayout(self.sheet_layout)  

        self.label = QLabel("Received Data:") 
        left_layout.addWidget(self.label)  

        self.result_table = QTableWidget()  
        left_layout.addWidget(self.result_table)

        right_widget = QWidget() 
        right_widget.setFixedWidth(700)
        right_layout = QVBoxLayout(right_widget)  
        splitter.addWidget(right_widget)

        buttons_layout = QHBoxLayout()  

        self.edit_button = QPushButton("Edit Image")
        self.edit_button.clicked.connect(self.convert_to_grayscale)  
        self.edit_button.setFixedHeight(35)  
        self.edit_button.setVisible(False)
        buttons_layout.addWidget(self.edit_button)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_image)  
        self.send_button.setFixedHeight(35)  
        self.send_button.setVisible(False)
        buttons_layout.addWidget(self.send_button)

        right_layout.addLayout(buttons_layout)

        self.image_label_title = QLabel("") 
        right_layout.addWidget(self.image_label_title)

        self.image_label = QLabel("No image received")  
        right_layout.addWidget(self.image_label)

        self.show()  
    
    def start_server(self):
        server_ip = '127.0.0.1'  
        server_port = 12345  
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        server_socket.bind((server_ip, server_port))  
        server_socket.listen(1)  

        while True:
            try:
                client_socket, _ = server_socket.accept()  
                data = b''
                while True:
                    part = client_socket.recv(1024)  
                    if not part:
                        break
                    data += part
                
                if data.startswith(b'{'):
                    json_data = json.loads(data.decode('utf-8')) 
                    self.process_json(json_data)
                else:
                    self.process_image(data) 
            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

    def process_json(self, json_data):
        if 'data' not in json_data:
            QMessageBox.critical(self, "Error", "Invalid data format received from server.")
            return
        self.result_table.setRowCount(0)
        columns = list(json_data['data'][0].keys())
        self.result_table.setColumnCount(len(columns) + 1)
        self.result_table.setHorizontalHeaderLabels(columns + ['Action'])
        
        for i, row_data in enumerate(json_data['data']):
            self.result_table.insertRow(i)
            for j, column in enumerate(columns):
                self.result_table.setItem(i, j, QTableWidgetItem(str(row_data[column])))
            
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda _, row=i: self.delete_row(row)) 
            self.result_table.setCellWidget(i, len(columns), delete_button)

    def delete_row(self, row):
        try:
            row_data = {}
            for column in range(self.result_table.columnCount() - 1):
                item = self.result_table.item(row, column)
                if item is not None:
                    row_data[self.result_table.horizontalHeaderItem(column).text()] = item.text()
            
            server_ip = '127.0.0.1'
            server_port = 12345  
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                delete_request = json.dumps({"action": "delete", "data": row_data}).encode('utf-8')
                s.sendall(delete_request)
            
            self.result_table.removeRow(row)
            QMessageBox.information(self, "Success", "Row deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the row: {e}")

    def process_image(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.image_label.setPixmap(pixmap)
        self.image_label_title.setText("Received Image")
        self.send_button.setVisible(True)
        self.edit_button.setVisible(True)

    def choose_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Images (*.png *.xpm *.jpg);;All Files (*)", options=options)
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("Chosen Image:")
            self.send_button.setVisible(True)
            self.edit_button.setVisible(True)

    def qimage_to_cvimage(self, qimage):
        qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        arr = np.array(ptr).reshape((height, width, 4))
        return arr[:, :, :3]  # Drop the alpha channel

    def convert_to_grayscale(self):
        if self.image_label.pixmap() is None:
            QMessageBox.warning(self, "No Image", "Please choose an image first.")
            return
        
        qimage = self.image_label.pixmap().toImage()
        cv_image = self.qimage_to_cvimage(qimage)
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        qimage = QImage(gray_image.data, gray_image.shape[1], gray_image.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)

    def send_image(self):
        try:
            if self.image_label.pixmap() is None:
                QMessageBox.warning(self, "No Image", "Please choose and edit an image first.")
                return

            pixmap = self.image_label.pixmap()
            image = pixmap.toImage()
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            image.save(buffer, "PNG")
            image_data = buffer.data()

            server_ip = '127.0.0.1'
            server_port = 12345

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(image_data)

            QMessageBox.information(self, "Success", "Edited image sent to server.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_app = ClientApp()
    sys.exit(app.exec_())
