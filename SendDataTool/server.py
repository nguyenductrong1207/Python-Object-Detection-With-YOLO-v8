import sys
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox
)

class SearchAndCountMoneyRepeatTime(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.observer = Observer()

    def init_ui(self):
        self.setWindowTitle("Search And Count Money Repeat Time")
        self.setFixedSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

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
        layout.addLayout(file_layout)

        sheet_and_money_layout = QHBoxLayout()
        self.sheet_label = QLabel("Sheet name:")
        self.sheet_combo = QComboBox()
        self.money_label = QLabel("Money amount:")
        self.money_edit = QLineEdit()

        self.sheet_combo.setFixedWidth(300)
        self.sheet_combo.setFixedHeight(35)
        self.money_edit.setFixedWidth(300)
        self.money_edit.setFixedHeight(35)

        sheet_and_money_layout.addWidget(self.sheet_label)
        sheet_and_money_layout.addWidget(self.sheet_combo)
        sheet_and_money_layout.addWidget(self.money_label)
        sheet_and_money_layout.addWidget(self.money_edit)
        layout.addLayout(sheet_and_money_layout)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_money)
        self.search_button.setFixedHeight(35)
        layout.addWidget(self.search_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setFixedHeight(35)
        layout.addWidget(self.clear_button)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_all_data)
        self.send_button.setFixedHeight(35)
        layout.addWidget(self.send_button)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name", "Action"])
        layout.addWidget(self.result_table)

        self.show()

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            self.file_edit.setText(file_path)
            self.load_sheets(file_path)
            self.result_table.setRowCount(0)
            self.start_watching(file_path)

    def load_sheets(self, file_path):
        try:
            excel_file = pd.ExcelFile(file_path)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(excel_file.sheet_names)
            self.sheet_combo.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read Excel file: {e}")

    def start_watching(self, file_path):
        event_handler = FileChangeHandler(self.send_data, file_path)
        self.observer.schedule(event_handler, path=file_path, recursive=False)
        self.observer.start()

    def send_data(self, file_path):
        try:
            server_ip = '127.0.0.1'
            server_port = 12345
            with open(file_path, 'rb') as file:
                data = file.read()
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(data)
            print(f"Data sent to {server_ip}:{server_port}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def send_all_data(self):
        try:
            data = {
                "file_path": self.file_edit.text(),
                "sheet_name": self.sheet_combo.currentText(),
                "money_amount": self.money_edit.text(),
                "results": []
            }
            for row in range(self.result_table.rowCount()):
                result = {
                    "money": self.result_table.item(row, 0).text(),
                    "time_repeated": self.result_table.item(row, 1).text(),
                    "total": self.result_table.item(row, 2).text(),
                    "sheet_name": self.result_table.item(row, 3).text(),
                }
                data["results"].append(result)

            server_ip = '127.0.0.1'
            server_port = 12345
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_port))
                s.sendall(json.dumps(data).encode('utf-8'))
            print(f"All Data sent to {server_ip}:{server_port}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def search_money(self):
        file_path = self.file_edit.text()
        sheet_name = self.sheet_combo.currentText()
        money_amount = self.money_edit.text()

        if not file_path or not money_amount:
            QMessageBox.warning(self, "Warning", "Please enter the file path and money amount.")
            return

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read Excel file: {e}")
            return

        if money_amount.isdigit():
            money_amount = int(money_amount)
        else:
            try:
                money_amount = float(money_amount.replace(',', ''))
            except ValueError:
                QMessageBox.critical(self, "Error", "Invalid money amount format.")
                return

        flat_list = df.values.flatten()
        count = (flat_list == money_amount).sum()

        row_position = 0
        self.result_table.insertRow(row_position)
        self.result_table.setItem(row_position, 0, QTableWidgetItem(f"{money_amount:,}"))
        if count == 0:
            self.result_table.setItem(row_position, 1, QTableWidgetItem("Non-existence"))
            self.result_table.setItem(row_position, 2, QTableWidgetItem(""))
        else:
            self.result_table.setItem(row_position, 1, QTableWidgetItem(str(count)))
            self.result_table.setItem(row_position, 2, QTableWidgetItem(f"{money_amount * count:,}"))

        self.result_table.setItem(row_position, 3, QTableWidgetItem(sheet_name))

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.confirm_delete_row(row_position))
        self.result_table.setCellWidget(row_position, 4, delete_button)

    def confirm_delete_row(self, row):
        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this row?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.result_table.removeRow(row)

    def clear_results(self):
        reply = QMessageBox.question(self, 'Confirm Clear', 'Are you sure you want to clear the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.result_table.setRowCount(0)
            self.file_edit.clear()
            self.money_edit.clear()
            self.sheet_combo.clear()
            self.sheet_combo.setVisible(False)

    def closeEvent(self, event):
        self.observer.stop()
        self.observer.join()
        event.accept()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback, file_path):
        self.callback = callback
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path == self.file_path:
            self.callback(event.src_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchAndCountMoneyRepeatTime()
    sys.exit(app.exec_())
