import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QSplitter
)
from PyQt5.QtCore import Qt

class IssueAnInvoice(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df_dict = {}  # Dictionary to store dataframes for each sheet
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Issue An Invoice")
        self.setFixedSize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Splitter to divide the UI into left and right parts
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Right side widget setup
        right_widget = QWidget()
        right_widget.setFixedWidth(700)
        right_left_layout = QVBoxLayout(right_widget)
        splitter.addWidget(right_widget)

        # Layout for file selection
        right_file_layout = QHBoxLayout()
        self.right_file_label = QLabel("Excel file path:")
        self.right_file_edit = QLineEdit()
        self.right_browse_button = QPushButton("Browse")
        self.right_browse_button.clicked.connect(self.right_browse_file)

        self.right_file_edit.setFixedHeight(35)
        self.right_browse_button.setFixedWidth(130)
        self.right_browse_button.setFixedHeight(35)

        right_file_layout.addWidget(self.right_file_label)
        right_file_layout.addWidget(self.right_file_edit)
        right_file_layout.addWidget(self.right_browse_button)
        
        right_left_layout.addLayout(right_file_layout)
        
        # Layout for choosing which are begin column and rows to start searching
        self.right_separate_label = QLabel("    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        self.right_input_label = QLabel("    Enter column and row for searching")
        right_left_layout.addWidget(self.right_separate_label)
        right_left_layout.addWidget(self.right_input_label)
        
        right_input_layout = QHBoxLayout()
        
        # 
        right_sheet_layout = QVBoxLayout()
        self.right_sheet_label = QLabel("Sheet name:")
        self.right_sheet_combo = QComboBox()
        self.right_sheet_combo.setFixedHeight(30)
        self.right_sheet_combo.setFixedWidth(200)

        right_sheet_layout.addWidget(self.right_sheet_label)
        right_sheet_layout.addWidget(self.right_sheet_combo)
        
        #
        right_row_start_layout = QVBoxLayout()
        self.right_row_start_label = QLabel("Row Start")        
        self.right_row_start_edit = QLineEdit()
        self.right_row_start_edit.setText("14")
        self.right_row_start_edit.setFixedHeight(30)
        self.right_row_start_edit.setFixedWidth(200)
        
        right_row_start_layout.addWidget(self.right_row_start_label)
        right_row_start_layout.addWidget(self.right_row_start_edit) 
        
        #
        right_row_end_layout = QVBoxLayout()
        self.right_row_end_label = QLabel("Row End")        
        self.right_row_end_edit = QLineEdit()
        self.right_row_end_edit.setFixedHeight(30)
        self.right_row_end_edit.setFixedWidth(200)
        
        right_row_end_layout.addWidget(self.right_row_end_label)
        right_row_end_layout.addWidget(self.right_row_end_edit) 
        
        right_input_layout.addLayout(right_sheet_layout)
        right_input_layout.addLayout(right_row_start_layout)
        right_input_layout.addLayout(right_row_end_layout)
        
        right_left_layout.addLayout(right_input_layout)
        
        # Layout for clear and search buttons
        right_buttons_layout = QHBoxLayout()
        self.right_clear_button = QPushButton("Clear")
        self.right_clear_button.clicked.connect(self.right_clear_results)
        self.right_clear_button.setFixedHeight(35)
        self.right_clear_button.setFixedWidth(200)
        right_buttons_layout.addWidget(self.right_clear_button)

        self.right_search_button = QPushButton("Search")
        self.right_search_button.clicked.connect(self.right_search_money)
        self.right_search_button.setFixedHeight(35)
        self.right_search_button.setFixedWidth(200)
        right_buttons_layout.addWidget(self.right_search_button)
        
        self.right_export_excel_button = QPushButton("Export Excel")
        self.right_export_excel_button.clicked.connect(self.right_export_excel)
        self.right_export_excel_button.setFixedHeight(35)
        self.right_export_excel_button.setFixedWidth(200)
        right_buttons_layout.addWidget(self.right_export_excel_button)
        
        right_left_layout.addLayout(right_buttons_layout)
        
        # Totol money in table
        self.right_total_label = QLabel("")
        self.right_total_label.setVisible(False)
        right_left_layout.addWidget(self.right_total_label)

        # Table to display results
        self.right_result_table = QTableWidget()
        self.right_result_table.setColumnCount(3)
        self.right_result_table.setFixedWidth(700)
        self.right_result_table.setHorizontalHeaderLabels(["Số Lượng", "Đơn Giá", "Thành Tiền"])
        self.right_result_table.setSortingEnabled(True)  # Enable sorting
        self.right_result_table.horizontalHeader().sectionClicked.connect(self.right_on_header_clicked)  # Connect header click

        right_left_layout.addWidget(self.right_result_table)

        self.show()

    # Open file dialog to select Excel file
    def right_browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xls *.xlsx)")
        if file_path:
            self.right_file_edit.setText(file_path)
            self.right_load_sheets(file_path)

    # Load all sheets from the selected Excel file into df_dict
    def right_load_sheets(self, file_path):
        try:
            self.df_dict = pd.read_excel(file_path, sheet_name=None)
            self.right_sheet_combo.clear()
            self.right_sheet_combo.addItems(self.df_dict.keys())
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Clear the results table and other inputs
    def right_clear_results(self):
        reply = QMessageBox.question(self, 'Confirm Clear', 'Are you sure you want to clear the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.right_result_table.setRowCount(0)
            # self.right_file_edit.clear()
            # self.right_sheet_combo.clear()

    # Search and show all the money in ascending order and the repeated time 
    def right_search_money(self):
        try:
            sheet_name = self.right_sheet_combo.currentText()
            if not sheet_name:
                QMessageBox.warning(self, "Warning", "Please select a sheet name.")
                return                  
            
            # Convert user input to zero-based indices 
            money_column_index = 5
            row_start_index = int(self.right_row_start_edit.text()) - 2
            row_end_index = int(self.right_row_end_edit.text()) - 1
            
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
            result.columns = ['Đơn Giá', 'Số Lượng']

            # Sort by Money in ascending order
            result = result.sort_values(by='Đơn Giá')

            # Add a 'Total' column
            result['Thành Tiền'] = result['Đơn Giá'] * result['Số Lượng']

            # Clear the table before adding new rows
            self.right_result_table.setRowCount(0)

            # Display the sorted results in the table 
            self.right_result_table.setRowCount(len(result))
            for row_idx, row_data in result.iterrows():
                self.right_result_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['Số Lượng'])))
                self.right_result_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['Đơn Giá'])))
                self.right_result_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['Thành Tiền'])))
                
            # Calculate the sum of the 'Total' column
            self.right_total_label.setText(f"    Total Cost: {result['Thành Tiền'].sum()}")
            self.right_total_label.setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # Slot for handling header click and sorting
    def right_on_header_clicked(self, logicalIndex):
        self.right_result_table.sortItems(logicalIndex, Qt.AscendingOrder)
     
    # Export new excel file due to the current table data    
    def right_export_excel(self):
        try:
            # Create a list to store the data
            data = []
            for row in range(self.right_result_table.rowCount()):
                row_data = []
                for column in range(self.right_result_table.columnCount()):
                    item = self.right_result_table.item(row, column)
                    text = item.text() if item is not None else ''
                    # Try to convert the text to a number
                    try:
                        number = float(text)
                        row_data.append(number)
                    except ValueError:
                        row_data.append(text)
                data.append(row_data)

            # Convert the list to a DataFrame
            df = pd.DataFrame(data, columns=["Số Lượng", "Đơn Giá", "Thành Tiền"])

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
    search_and_count_app = IssueAnInvoice()
    sys.exit(app.exec_())
