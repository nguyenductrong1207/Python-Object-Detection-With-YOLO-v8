import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox
)

class SearchAndCountMoneyRepeatTime(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

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

        # Set fixed heights for the edit field and button
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

        # Set fixed heights and widths for the combo box and edit field
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
            self.result_table.setRowCount(0)  # Clear old results

    def load_sheets(self, file_path):
        try:
            excel_file = pd.ExcelFile(file_path)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(excel_file.sheet_names)
            self.sheet_combo.setVisible(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read Excel file: {e}")

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
        
        # self.result_table.setRowCount(0)  # Clear all result for each time

        # Insert new rows at the end of the table
        # row_position = self.result_table.rowCount() 

        row_position = 0  # Insert new row at the beginning of the table
        self.result_table.insertRow(row_position)
        self.result_table.setItem(row_position, 0, QTableWidgetItem(f"{money_amount:,}"))
        if count == 0:
            self.result_table.setItem(row_position, 1, QTableWidgetItem("Non-existence"))
            self.result_table.setItem(row_position, 2, QTableWidgetItem(""))
        else:
            self.result_table.setItem(row_position, 1, QTableWidgetItem(str(count)))
            self.result_table.setItem(row_position, 2, QTableWidgetItem(f"{money_amount * count:,}"))

        self.result_table.setItem(row_position, 3, QTableWidgetItem(sheet_name))

        # Add Delete Button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.confirm_delete_row(row_position))
        self.result_table.setCellWidget(row_position, 4, delete_button)

    def confirm_delete_row(self, row):
        reply = QMessageBox.question(self, 'Confirm Delete',
                                     'Are you sure you want to delete this row?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.result_table.removeRow(row)

    def clear_results(self):
        reply = QMessageBox.question(self, 'Confirm Clear',
                                     'Are you sure you want to clear the results?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.result_table.setRowCount(0)
            self.file_edit.clear()
            self.money_edit.clear()
            self.sheet_combo.clear()
            self.sheet_combo.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchAndCountMoneyRepeatTime()
    sys.exit(app.exec_())
