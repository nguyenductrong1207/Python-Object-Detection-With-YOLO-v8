import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QSplitter
)
from PyQt5.QtCore import Qt

class FindDataToIssueAnInvoice(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_dict = {}  # Dictionary to store dataframes for each sheet
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Search And Count Money Repeat Time")
        self.setFixedSize(1000, 700)

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
        
        # Layout for choosing which are begin column and rows to start searching
        self.separate_label = QLabel("    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        self.input_label = QLabel("    Enter column and row for searching")
        left_layout.addWidget(self.separate_label)
        left_layout.addWidget(self.input_label)
        
        input_layout = QHBoxLayout()
        
        column_layout = QVBoxLayout()
        self.column_label = QLabel("Column Index")        
        self.column_edit = QLineEdit()
        self.column_edit.setFixedHeight(30)
        self.column_edit.setFixedWidth(200)
        
        column_layout.addWidget(self.column_label)
        column_layout.addWidget(self.column_edit) 
        
        row_start_layout = QVBoxLayout()
        self.row_start_label = QLabel("Row Start")        
        self.row_start_edit = QLineEdit()
        self.row_start_edit.setFixedHeight(30)
        self.row_start_edit.setFixedWidth(200)
        
        row_start_layout.addWidget(self.row_start_label)
        row_start_layout.addWidget(self.row_start_edit) 
        
        row_end_layout = QVBoxLayout()
        self.row_end_label = QLabel("Row End")        
        self.row_end_edit = QLineEdit()
        self.row_end_edit.setFixedHeight(30)
        self.row_end_edit.setFixedWidth(200)
        
        row_end_layout.addWidget(self.row_end_label)
        row_end_layout.addWidget(self.row_end_edit) 
        
        input_layout.addLayout(column_layout)
        input_layout.addLayout(row_start_layout)
        input_layout.addLayout(row_end_layout)
        
        left_layout.addLayout(input_layout)
        
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
        
        self.export_excel_button = QPushButton("Export Excel")
        self.export_excel_button.clicked.connect(self.export_excel)
        self.export_excel_button.setFixedHeight(35)
        self.export_excel_button.setFixedWidth(200)
        buttons_layout.addWidget(self.export_excel_button)
        
        left_layout.addLayout(buttons_layout)
        
        # Layout for choosing which are begin column and rows to start searching
        self.total_label = QLabel("")
        self.total_label.setVisible(False)
        left_layout.addWidget(self.total_label)

        # Table to display results
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setFixedWidth(700)
        self.result_table.setHorizontalHeaderLabels(["Time Repeated", "Money", "Total"])
        self.result_table.setSortingEnabled(True)  # Enable sorting
        self.result_table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)  # Connect header click

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
            # self.file_edit.clear()
            # self.sheet_combo.clear()

    # Search and show all the money in ascending order and the repeated time 
    def search_money(self):
        try:
            sheet_name = self.sheet_combo.currentText()
            if not sheet_name:
                QMessageBox.warning(self, "Warning", "Please select a sheet name.")
                return                  
            
            # Convert user input to zero-based indices 
            money_column_index = int(self.column_edit.text()) - 1
            row_start_index = int(self.row_start_edit.text()) - 2
            row_end_index = int(self.row_end_edit.text()) - 1
            
            # Subset the DataFrame to the specified rows 
            df = self.df_dict[sheet_name]
            df = df.iloc[row_start_index:row_end_index]

            # Extract the money column and drop NaN values 
            if len(df.columns) <= money_column_index:
                QMessageBox.critical(self, "Error", f"Sheet {sheet_name} does not have enough columns.")
                return
            
            money_column = df.iloc[:, money_column_index]
            money_column = money_column.dropna()

            # Count occurrences of each money amount
            result = money_column.value_counts().reset_index()
            result.columns = ['Money', 'Time Repeated']

            # Sort by Money in ascending order
            result = result.sort_values(by='Money')

            # Add a 'Total' column
            result['Total'] = result['Money'] * result['Time Repeated']

            # Clear the table before adding new rows
            self.result_table.setRowCount(0)

            # Display the sorted results in the table 
            self.result_table.setRowCount(len(result))
            for row_idx, row_data in result.iterrows():
                self.result_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['Time Repeated'])))
                self.result_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['Money'])))
                self.result_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['Total'])))
                
            # Calculate the sum of the 'Total' column
            self.total_label.setText(f"    Sum of Total Amount: {result['Total'].sum()}")
            self.total_label.setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Slot for handling header click and sorting
    def on_header_clicked(self, logicalIndex):
        self.result_table.sortItems(logicalIndex, Qt.AscendingOrder)
     
    # Export new excel file due to the current table data    
    def export_excel(self):
        try:
            # Create a list to store the data
            data = []
            for row in range(self.result_table.rowCount()):
                row_data = []
                for column in range(self.result_table.columnCount()):
                    item = self.result_table.item(row, column)
                    text = item.text() if item is not None else ''
                    # Try to convert the text to a number
                    try:
                        number = float(text)
                        row_data.append(number)
                    except ValueError:
                        row_data.append(text)
                data.append(row_data)

            # Convert the list to a DataFrame
            df = pd.DataFrame(data, columns=["Time Repeated", "Money", "Total"])

            # Prompt the user to select a save location and filename
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            if file_path:
                # Use xlsxwriter to write the DataFrame to Excel with formatting
                writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')

                # Access the workbook and worksheet
                workbook  = writer.book
                worksheet = writer.sheets['Sheet1']

                # Define the format for Times New Roman with font size 11
                cell_format = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 11})

                # Apply the format to all cells
                for row_num in range(len(df) + 1):  # +1 for the header
                    for col_num in range(len(df.columns)):
                        if row_num == 0:
                            worksheet.write(row_num, col_num, df.columns[col_num], cell_format)
                        else:
                            worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], cell_format)

                # Close the Pandas Excel writer and output the Excel file.
                writer.close()
                QMessageBox.information(self, "Success", f"File saved to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    search_and_count_app = FindDataToIssueAnInvoice()
    sys.exit(app.exec_())
