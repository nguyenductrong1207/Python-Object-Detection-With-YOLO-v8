import sys
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QSplitter
)
from PyQt5.QtGui import QPixmap

class SearchAndCountMoneyRepeatTime(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.observer = Observer()

    def init_ui(self):
        self.setWindowTitle("Search And Count Money Repeat Time")
        self.setFixedSize(1400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Splitter to divide left and right parts
        splitter = QSplitter()
        layout.addWidget(splitter)
        
        left_widget = QWidget()
        left_widget.setFixedWidth(700)
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)
        
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Excel file path:")
        self.file_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        self.file_edit.setFixedHeight(35)
        self.browse_button.setFixedWidth(130)
        self.browse_button.setFixedHeight(35)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_button)
        left_layout.addLayout(file_layout)

        sheet_and_money_layout = QHBoxLayout()
        self.sheet_label = QLabel("Sheet name:")
        self.sheet_combo = QComboBox()
        self.money_label = QLabel("Money amount:")
        self.money_edit = QLineEdit()

        self.sheet_combo.setFixedWidth(240)
        self.sheet_combo.setFixedHeight(35)
        self.money_edit.setFixedWidth(240)
        self.money_edit.setFixedHeight(35)

        sheet_and_money_layout.addWidget(self.sheet_label)
        sheet_and_money_layout.addWidget(self.sheet_combo)
        sheet_and_money_layout.addWidget(self.money_label)
        sheet_and_money_layout.addWidget(self.money_edit)
        left_layout.addLayout(sheet_and_money_layout)

        buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setFixedHeight(35)
        self.clear_button.setFixedWidth(200)
        buttons_layout.addWidget(self.clear_button)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_money)
        self.search_button.setFixedHeight(35)
        self.search_button.setFixedWidth(200)
        buttons_layout.addWidget(self.search_button)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_all_data)
        self.send_button.setFixedHeight(35)
        self.send_button.setFixedWidth(200)
        buttons_layout.addWidget(self.send_button)
        
        left_layout.addLayout(buttons_layout)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setFixedWidth(700)
        self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name", "Action"])
        left_layout.addWidget(self.result_table)

        # Right part for image selection and display
        right_widget = QWidget()
        right_widget.setFixedWidth(700)
        right_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)
        
        image_buttons_layout = QHBoxLayout()
        self.choose_image_button = QPushButton("Choose Image")
        self.choose_image_button.clicked.connect(self.choose_image)
        self.send_image_button = QPushButton("Send Image")
        self.send_image_button.clicked.connect(self.send_image)
        
        self.choose_image_button.setFixedHeight(35)
        self.send_image_button.setFixedHeight(35)

        image_buttons_layout.addWidget(self.choose_image_button)
        image_buttons_layout.addWidget(self.send_image_button)
        right_layout.addLayout(image_buttons_layout)

        self.image_label = QLabel("No image selected")
        right_layout.addWidget(self.image_label)
        
        self.show()

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            self.file_edit.setText(file_path)
            self.load_sheets(file_path)

    def load_sheets(self, file_path):
        try:
            self.df_dict = pd.read_excel(file_path, sheet_name=None)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(self.df_dict.keys())
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def clear_results(self):
        self.result_table.setRowCount(0)
        self.file_edit.clear()
        self.sheet_combo.clear()
        self.money_edit.clear()

    def search_money(self):
        money_amount = self.money_edit.text().strip()
        if not money_amount:
            QMessageBox.warning(self, "Input Error", "Please enter a money amount.")
            return

        current_sheet = self.sheet_combo.currentText()
        df = self.df_dict[current_sheet]

        result = df[df.apply(lambda row: row.astype(str).str.contains(money_amount).any(), axis=1)]
        count = len(result)

        row_position = self.result_table.rowCount()
        self.result_table.insertRow(row_position)
        self.result_table.setItem(row_position, 0, QTableWidgetItem(money_amount))
        self.result_table.setItem(row_position, 1, QTableWidgetItem(str(count)))
        self.result_table.setItem(row_position, 2, QTableWidgetItem(str(count * float(money_amount))))
        self.result_table.setItem(row_position, 3, QTableWidgetItem(current_sheet))

        send_button = QPushButton("Send")
        send_button.clicked.connect(lambda: self.send_single_data(money_amount, count, count * float(money_amount), current_sheet))
        self.result_table.setCellWidget(row_position, 4, send_button)

    def send_single_data(self, money, count, total, sheet_name):
        try:
            server_ip = '127.0.0.1'  # Replace with the client's IP address
            server_port = 12345
            data = {
                'file_path': self.file_edit.text(),
                'sheet_name': sheet_name,
                'results': [{'money': money, 'time_repeated': str(count), 'total': str(total), 'sheet_name': sheet_name}]
            }
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(json.dumps(data).encode('utf-8'))
            QMessageBox.information(self, "Success", "Data sent to client.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def send_all_data(self):
        try:
            server_ip = '127.0.0.1'  # Replace with the client's IP address
            server_port = 12345
            data = {
                'file_path': self.file_edit.text(),
                'sheet_name': self.sheet_combo.currentText(),
                'results': []
            }
            for row in range(self.result_table.rowCount()):
                money = self.result_table.item(row, 0).text()
                time_repeated = self.result_table.item(row, 1).text()
                total = self.result_table.item(row, 2).text()
                sheet_name = self.result_table.item(row, 3).text()
                data['results'].append({
                    'money': money,
                    'time_repeated': time_repeated,
                    'total': total,
                    'sheet_name': sheet_name
                })
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(json.dumps(data).encode('utf-8'))
            QMessageBox.information(self, "Success", "All data sent to client.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def choose_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path).scaled(600, 600, aspectRatioMode=1)
            self.image_label.setPixmap(pixmap)
            self.image_label.setText("")

    def send_image(self):
        try:
            if not hasattr(self, 'image_path'):
                QMessageBox.warning(self, "No Image", "Please choose an image first.")
                return

            server_ip = '127.0.0.1'  # Replace with the client's IP address
            server_port = 12345
            with open(self.image_path, "rb") as image_file:
                image_data = image_file.read()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(image_data)
            QMessageBox.information(self, "Success", "Image sent to client.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_modified(self, event):
        if event.src_path == self.file_edit.text():
            self.load_sheets(self.file_edit.text())

    def start_watching(self, file_path):
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = self.on_modified
        self.observer.schedule(event_handler, file_path, recursive=False)
        self.observer.start()

    def stop_watching(self):
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    search_and_count_app = SearchAndCountMoneyRepeatTime()
    sys.exit(app.exec_())
