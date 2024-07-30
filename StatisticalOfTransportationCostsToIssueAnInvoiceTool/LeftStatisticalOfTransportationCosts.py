import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QSplitter
)
from PyQt5.QtCore import Qt

class StatisticalOfTransportationCosts(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_dict = {}  # Dictionary to store dataframes for each sheet
        self.init_ui()
        self.left_total_cost = 0
        self.left_total_weight = 0

    def init_ui(self):
        self.setWindowTitle("Statistical Of Transportation Costs")
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
        left_file_layout = QHBoxLayout()
        self.left_file_label = QLabel("Excel file path:")
        self.left_file_edit = QLineEdit()
        self.left_browse_button = QPushButton("Browse")
        self.left_browse_button.clicked.connect(self.left_browse_file)

        self.left_file_edit.setFixedHeight(35)
        self.left_browse_button.setFixedWidth(130)
        self.left_browse_button.setFixedHeight(35)

        left_file_layout.addWidget(self.left_file_label)
        left_file_layout.addWidget(self.left_file_edit)
        left_file_layout.addWidget(self.left_browse_button)
        
        left_layout.addLayout(left_file_layout)
        
        # Layout for choosing which are begin column and rows to start searching
        self.left_separate_label = QLabel("    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        self.left_input_label = QLabel("    Enter column and row for searching")
        left_layout.addWidget(self.left_separate_label)
        left_layout.addWidget(self.left_input_label)
        
        left_input_layout = QHBoxLayout()
        
        # 
        left_sheet_layout = QVBoxLayout()
        self.left_sheet_label = QLabel("Sheet name:")
        self.left_sheet_combo = QComboBox()
        self.left_sheet_combo.setFixedHeight(30)
        self.left_sheet_combo.setFixedWidth(200)

        left_sheet_layout.addWidget(self.left_sheet_label)
        left_sheet_layout.addWidget(self.left_sheet_combo)
        
        #
        left_row_start_layout = QVBoxLayout()
        self.left_row_start_label = QLabel("Row Start")        
        self.left_row_start_edit = QLineEdit()
        self.left_row_start_edit.setText("8")
        self.left_row_start_edit.setFixedHeight(30)
        self.left_row_start_edit.setFixedWidth(200)
        
        left_row_start_layout.addWidget(self.left_row_start_label)
        left_row_start_layout.addWidget(self.left_row_start_edit) 
        
        #
        left_row_end_layout = QVBoxLayout()
        self.left_row_end_label = QLabel("Row End")        
        self.left_row_end_edit = QLineEdit()
        self.left_row_end_edit.setFixedHeight(30)
        self.left_row_end_edit.setFixedWidth(200)
        
        left_row_end_layout.addWidget(self.left_row_end_label)
        left_row_end_layout.addWidget(self.left_row_end_edit) 
        
        #
        left_input_layout.addLayout(left_sheet_layout)
        left_input_layout.addLayout(left_row_start_layout)
        left_input_layout.addLayout(left_row_end_layout)
        
        left_layout.addLayout(left_input_layout)
        
        # Layout for clear and search buttons
        left_buttons_layout = QHBoxLayout()
        self.left_clear_button = QPushButton("Clear")
        self.left_clear_button.clicked.connect(self.left_clear_results)
        self.left_clear_button.setFixedHeight(35)
        self.left_clear_button.setFixedWidth(200)
        left_buttons_layout.addWidget(self.left_clear_button)

        self.left_search_button = QPushButton("Search")
        self.left_search_button.clicked.connect(self.left_search_money)
        self.left_search_button.setFixedHeight(35)
        self.left_search_button.setFixedWidth(200)
        left_buttons_layout.addWidget(self.left_search_button)
        
        self.left_export_excel_button = QPushButton("Export Excel")
        self.left_export_excel_button.clicked.connect(self.left_export_excel)
        self.left_export_excel_button.setFixedHeight(35)
        self.left_export_excel_button.setFixedWidth(200)
        left_buttons_layout.addWidget(self.left_export_excel_button)
        
        left_layout.addLayout(left_buttons_layout)
        
        # Totol money in table
        self.left_total_cost_label = QLabel("")
        self.left_total_cost_label.setVisible(False)
        left_layout.addWidget(self.left_total_cost_label)
        
        # Totol weight in table
        self.left_total_weight_label = QLabel("")
        self.left_total_weight_label.setVisible(False)
        left_layout.addWidget(self.left_total_weight_label)

        # Table to display results
        self.left_result_table = QTableWidget()
        self.left_result_table.setColumnCount(4)
        self.left_result_table.setFixedWidth(700)
        self.left_result_table.setHorizontalHeaderLabels(["Ngày Xuất", "Điểm Giao Hàng", "Trọng Lượng", "Giá Vận Chuyển"])
        # self.left_result_table.setSortingEnabled(True)  # Enable sorting
        # self.left_result_table.horizontalHeader().sectionClicked.connect(self.left_on_header_clicked)  # Connect header click

        left_layout.addWidget(self.left_result_table)

        self.show()

    # Open file dialog to select Excel file
    def left_browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            self.left_file_edit.setText(file_path)
            self.left_load_sheets(file_path)
            self.left_result_table.setRowCount(0)
            self.left_total_cost_label.setVisible(False)
            self.left_total_cost = 0
            self.left_total_weight = 0
            

    # Load all sheets from the selected Excel file into df_dict
    def left_load_sheets(self, file_path):
        try:
            self.df_dict = pd.read_excel(file_path, sheet_name=None)
            self.left_sheet_combo.clear()
            self.left_sheet_combo.addItems(self.df_dict.keys())
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Clear the results table and other inputs
    def left_clear_results(self):
        reply = QMessageBox.question(self, 'Confirm Clear', 'Are you sure you want to clear the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.left_result_table.setRowCount(0)
            self.left_total_cost_label.setVisible(False)
            self.left_total_cost = 0
            self.left_total_weight = 0

    # Search and show all data from all sheets and display all 
    def left_search_money(self):
        try:
            sheet_name = self.left_sheet_combo.currentText()
            row_start = int(self.left_row_start_edit.text())
            row_end = int(self.left_row_end_edit.text())

            if not sheet_name:
                QMessageBox.warning(self, "Warning", "Please select a sheet name.")
                return
            
            df = self.df_dict[sheet_name]

            date_column = df.iloc[row_start - 2 : row_end - 1, 1]  # Column B 
            location_column = df.iloc[row_start - 2 : row_end - 1, 5]  # Column F 

            # Ensure correct columns are referenced and handle NaN values
            weight_column_g = pd.to_numeric(df.iloc[row_start - 2 : row_end - 1, 6].fillna(0), errors='coerce')  # Column G (index 6)
            weight_column_i = pd.to_numeric(df.iloc[row_start - 2 : row_end - 1, 8].fillna(0), errors='coerce')  # Column I (index 8)
            weight_column = weight_column_g + weight_column_i  # Sum of Columns G and I

            cost_column = df.iloc[row_start - 2 : row_end - 1, 16]  # Column Q 

            # Keep track of the starting row index
            start_row = self.left_result_table.rowCount()

            for i in range(len(date_column)):
                date = date_column.iloc[i]
                location = location_column.iloc[i]
                weight = weight_column.iloc[i]
                cost = cost_column.iloc[i]
                
                # Convert values to strings, but keep them empty if NaN
                date_str = str(date) if pd.notna(date) else ""
                location_str = str(location) if pd.notna(location) else ""
                weight_str = str(weight) if pd.notna(weight) else ""
                cost_str = str(cost) if pd.notna(cost) else ""
                
                self.left_result_table.insertRow(start_row + i)
                self.left_result_table.setItem(start_row + i, 0, QTableWidgetItem(date_str))
                self.left_result_table.setItem(start_row + i, 1, QTableWidgetItem(location_str))
                self.left_result_table.setItem(start_row + i, 2, QTableWidgetItem(weight_str))
                self.left_result_table.setItem(start_row + i, 3, QTableWidgetItem(cost_str))
                
                # Calculate total cost only if cost is a valid number
                if cost_str and cost_str.replace('.', '', 1).isdigit():
                    self.left_total_cost += int(cost_str)
                    
                # Calculate total weight only if cost is a valid number
                if weight_str and weight_str.replace('.', '', 1).isdigit():
                    self.left_total_weight += int(weight_str)
                    
            self.left_total_cost_label.setText(f"Total Cost: {self.left_total_cost}")
            self.left_total_cost_label.setVisible(True)
            
            self.left_total_weight_label.setText(f"Total Weight: {self.left_total_weight}")
            self.left_total_weight_label.setVisible(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Slot for handling header click and sorting
    # def left_on_header_clicked(self, logicalIndex):
    #     self.left_result_table.sortItems(logicalIndex, Qt.AscendingOrder)
     
    # Export new excel file due to the current table data    
    def left_export_excel(self):
        try:
            # Create a list to store the data
            data = []
            for row in range(self.left_result_table.rowCount()):
                row_data = []
                for column in range(self.left_result_table.columnCount()):
                    item = self.left_result_table.item(row, column)
                    text = item.text() if item is not None else ''
                    # Try to convert the text to a number
                    try:
                        number = float(text)
                        row_data.append(number)
                    except ValueError:
                        row_data.append(text)
                data.append(row_data)

            # Convert the list to a DataFrame
            df = pd.DataFrame(data, columns=["Ngày Xuất", "Điểm Giao Hàng", "Trọng Lượng", "Giá Vận Chuyển"])

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
    search_and_count_app = StatisticalOfTransportationCosts()
    sys.exit(app.exec_())
