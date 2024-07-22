import sys
import socket
import threading
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSplitter
)
from PyQt5.QtGui import QPixmap

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

    def init_ui(self):
        self.setWindowTitle("Client View")
        self.setFixedSize(1400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Splitter to divide left and right parts
        splitter = QSplitter()
        layout.addWidget(splitter)
        
        # Left part for the existing UI
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

        # Right part for image display
        right_widget = QWidget()
        right_widget.setFixedWidth(700)
        right_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)

        self.image_label_title = QLabel("Image Sent")
        right_layout.addWidget(self.image_label_title)

        self.image_label = QLabel("No image received")
        right_layout.addWidget(self.image_label)

        self.show()

    def start_server(self):
        server_ip = '127.0.0.1'  # Replace with the server's IP address
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
                    self.display_data(data)
                else:
                    self.display_image(data)
                client_socket.close()
            except Exception as e:
                print(f"Error in server: {e}")

    def display_data(self, data):
        try:
            data = json.loads(data.decode('utf-8'))
            self.file_edit.setText(data['file_path'])
            self.sheet_combo.clear()
            self.sheet_combo.addItem(data['sheet_name'])
            self.sheet_combo.setCurrentText(data['sheet_name'])

            # self.result_table.setRowCount(0)  # Clear previous data
            self.result_table.setColumnCount(4)
            self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name"])

            for result in data['results']:
                row_position = self.result_table.rowCount()
                self.result_table.insertRow(row_position)
                self.result_table.setItem(row_position, 0, QTableWidgetItem(result['money']))
                self.result_table.setItem(row_position, 1, QTableWidgetItem(result['time_repeated']))
                self.result_table.setItem(row_position, 2, QTableWidgetItem(result['total']))
                self.result_table.setItem(row_position, 3, QTableWidgetItem(result['sheet_name']))

            # Make the table read-only
            self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        except Exception as e:
            print(f"Error displaying data: {e}")

    def display_image(self, data):
        try:
            with open("received_image.png", "wb") as file:
                file.write(data)
            pixmap = QPixmap("received_image.png").scaled(600, 600, aspectRatioMode=1)
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("")
        except Exception as e:
            print(f"Error displaying image: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_app = ClientApp()
    sys.exit(app.exec_())
