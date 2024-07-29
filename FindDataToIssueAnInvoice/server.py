import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QSplitter
)

class FindDataToIssueAnInvoice(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_dict = {}  # Dictionary to store dataframes for each sheet
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Search And Count Money Repeat Time")
        self.setFixedSize(1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Splitter to divide the UI into left and right parts
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left side widget setup
        left_widget = QWidget()
        left_widget.setFixedWidth(700)
        left_layout = QVBoxLayout(left_widget)
        splitter.addWidget(left_widget)

        # Layout for file selection
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

        # Layout for sheet name selection
        sheet_and_money_layout = QHBoxLayout()
        self.sheet_label = QLabel("Sheet name:")
        self.sheet_combo = QComboBox()

        self.sheet_combo.setFixedWidth(240)
        self.sheet_combo.setFixedHeight(35)

        sheet_and_money_layout.addWidget(self.sheet_label)
        sheet_and_money_layout.addWidget(self.sheet_combo)
        left_layout.addLayout(sheet_and_money_layout)

        # Layout for clear and search buttons
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
        left_layout.addLayout(buttons_layout)

        # Table to display results
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setFixedWidth(700)
        self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total"])
        left_layout.addWidget(self.result_table)

        self.show()

    # Open file dialog to select Excel file
    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            self.file_edit.setText(file_path)
            self.load_sheets(file_path)

    # Load all sheets from the selected Excel file into df_dict
    def load_sheets(self, file_path):
        try:
            
            self.df_dict = pd.read_excel(file_path, sheet_name=None)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(self.df_dict.keys())
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    # Clear the results table and other inputs
    def clear_results(self):
        
        reply = QMessageBox.question(self, 'Confirm Clear', 'Are you sure you want to clear the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.result_table.setRowCount(0)
            self.file_edit.clear()
            self.sheet_combo.clear()

    # Search and show all the money in ascending order and the repeated time 
    def search_money(self):
        try:
            sheet_name = self.sheet_combo.currentText()
            if not sheet_name:
                QMessageBox.warning(self, "Warning", "Please select a sheet name.")
                return

            # Select the dataframe for the chosen sheet and subset rows 14 to 215
            df = self.df_dict[sheet_name]
            df = df.iloc[12:214]

            # Column index for money data
            money_column_index = 5
            if len(df.columns) <= money_column_index:
                QMessageBox.critical(self, "Error", f"Sheet {sheet_name} does not have enough columns.")
                return

            # Extract the money column and drop NaN values
            money_column = df.iloc[:, money_column_index]
            money_column = money_column.dropna()

            # Count occurrences of each money amount
            result = money_column.value_counts().reset_index()
            result.columns = ['Money', 'Time Repeated']

            # Sort by Money in ascending order
            result = result.sort_values(by='Money')
            result['Total'] = result['Money'] * result['Time Repeated']

            # Display the sorted results in the table
            self.result_table.setRowCount(len(result))
            for row_idx, row_data in result.iterrows():
                self.result_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['Money'])))
                self.result_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['Time Repeated'])))
                self.result_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['Total'])))

            # Debug prints to verify sorting
            print(f"Sorted money counts:\n{result}")
            print(f"Total rows in result table: {self.result_table.rowCount()}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    search_and_count_app = FindDataToIssueAnInvoice()
    sys.exit(app.exec_())
