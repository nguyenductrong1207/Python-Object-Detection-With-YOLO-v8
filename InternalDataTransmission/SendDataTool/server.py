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

        buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setFixedHeight(35)
        self.clear_button.setFixedWidth(230)
        buttons_layout.addWidget(self.clear_button)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_money)
        self.search_button.setFixedHeight(35)
        self.search_button.setFixedWidth(230)
        buttons_layout.addWidget(self.search_button)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_all_data)
        self.send_button.setFixedHeight(35)
        self.send_button.setFixedWidth(230)
        buttons_layout.addWidget(self.send_button)
        
        layout.addLayout(buttons_layout)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name", "Action"])
        self.result_table.setColumnWidth(4, 200)  # Make the action column wider
        layout.addWidget(self.result_table)

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
            
    def start_watching(self, file_path):
        event_handler = FileChangeHandler(self.send_data, file_path)
        self.observer.schedule(event_handler, path=file_path, recursive=False)
        self.observer.start()

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

        action_layout = QHBoxLayout()
        
        send_button = QPushButton("Send")
        send_button.setFixedHeight(25)
        send_button.clicked.connect(lambda: self.send_single_data(money_amount, count, count * float(money_amount), current_sheet))
        action_layout.addWidget(send_button)
        
        delete_button = QPushButton("Delete")
        delete_button.setFixedHeight(25)
        delete_button.clicked.connect(lambda: self.confirm_delete_row(row_position))
        action_layout.addWidget(delete_button)
        
        action_widget = QWidget()
        action_widget.setLayout(action_layout)
        
        self.result_table.setCellWidget(row_position, 4, action_widget)

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
