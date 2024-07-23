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
        self.observer = Observer()  # Initialize the file observer

    def init_ui(self):
        self.setWindowTitle("Search And Count Money Repeat Time")  
        self.setFixedSize(1400, 600) 

        central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)  # Set a horizontal layout for the central widget ( by default )
        
        splitter = QSplitter()  # Create a splitter to divide the layout into 2 parts
        layout.addWidget(splitter)
        
        #########################################################################################
        
        # Create a widget for the left part
        left_widget = QWidget()  
        left_widget.setFixedWidth(700)  
        
        # Set a layout for the left widget
        left_layout = QVBoxLayout(left_widget)  
        
        # Add the left widget to the splitter
        splitter.addWidget(left_widget)  
        
        #########################################################################################
        
        # Create a layout for the file path and Button to browse for a file
        file_layout = QHBoxLayout()  
        self.file_label = QLabel("Excel file path:")  
        self.file_edit = QLineEdit()  
        self.browse_button = QPushButton("Browse")  
        self.browse_button.clicked.connect(self.browse_file)  

        self.file_edit.setFixedHeight(35) 
        self.browse_button.setFixedWidth(130)  
        self.browse_button.setFixedHeight(35)  

        # Add the file label, file edit, browse button to the file layout
        file_layout.addWidget(self.file_label)  
        file_layout.addWidget(self.file_edit)  
        file_layout.addWidget(self.browse_button) 
        
        # Add the file layout to the left layout
        left_layout.addLayout(file_layout)  
        
        #########################################################################################

        # Create a layout for the sheet name and money amount
        sheet_and_money_layout = QHBoxLayout()  
        self.sheet_label = QLabel("Sheet name:")  
        self.sheet_combo = QComboBox()  
        self.money_label = QLabel("Money amount:") 
        self.money_edit = QLineEdit()  

        self.sheet_combo.setFixedWidth(240) 
        self.sheet_combo.setFixedHeight(35)  
        self.money_edit.setFixedWidth(240)  
        self.money_edit.setFixedHeight(35) 

        # Add the sheet label, sheet combobox, money label, money edit to the layout
        sheet_and_money_layout.addWidget(self.sheet_label)  
        sheet_and_money_layout.addWidget(self.sheet_combo) 
        sheet_and_money_layout.addWidget(self.money_label) 
        sheet_and_money_layout.addWidget(self.money_edit)  
        
        # Add the sheet and money layout to the left layout
        left_layout.addLayout(sheet_and_money_layout)  

        #########################################################################################
        
        # Create a horizontal layout for the buttons
        buttons_layout = QHBoxLayout()  
        
        # Create clear button and add to the buttons layout
        self.clear_button = QPushButton("Clear")  
        self.clear_button.clicked.connect(self.clear_results) 
        self.clear_button.setFixedHeight(35) 
        self.clear_button.setFixedWidth(200) 
        buttons_layout.addWidget(self.clear_button)  
        
        # Create search button and add to the buttons layout
        self.search_button = QPushButton("Search") 
        self.search_button.clicked.connect(self.search_money)  
        self.search_button.setFixedHeight(35) 
        self.search_button.setFixedWidth(200) 
        buttons_layout.addWidget(self.search_button)  

        # Create send button and add to the buttons layout
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_all_data)  
        self.send_button.setFixedHeight(35)  
        self.send_button.setFixedWidth(200) 
        buttons_layout.addWidget(self.send_button) 
        
        # Add the buttons layout to the left layout
        left_layout.addLayout(buttons_layout)
        
        #########################################################################################

        # Create a table widget for displaying results
        self.result_table = QTableWidget()  
        
        # Set the number of columns in the table
        self.result_table.setColumnCount(5)  
        self.result_table.setFixedWidth(700)  
         # Set the column headers
        self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name", "Action"]) 
        # Set width for the action column 
        self.result_table.setColumnWidth(4, 150)  
        
        # Add the table to the left layout
        left_layout.addWidget(self.result_table)  
        
        #########################################################################################

        # Create a widget for the right part
        right_widget = QWidget()  # Create a widget for the right part
        right_widget.setFixedWidth(700)  
        
        # Set a layout for the right widget
        right_layout = QVBoxLayout(right_widget)  
        
        # Add the right widget to the splitter
        splitter.addWidget(right_widget)  
        
        #########################################################################################
        
        # Create a layout for the image buttons
        image_buttons_layout = QHBoxLayout()  
        
        # Create buttons to choose and send an image 
        self.choose_image_button = QPushButton("Choose Image")  
        self.choose_image_button.clicked.connect(self.choose_image) 
        self.send_image_button = QPushButton("Send Image") 
        self.send_image_button.clicked.connect(self.send_image)  
        
        self.choose_image_button.setFixedHeight(35) 
        self.send_image_button.setFixedHeight(35)  

        # Add the choose and send button to the image buttons layout
        image_buttons_layout.addWidget(self.choose_image_button)  
        image_buttons_layout.addWidget(self.send_image_button)  
        
        # Add the image buttons layout to the right layout
        right_layout.addLayout(image_buttons_layout) 
        
        #########################################################################################

        # Create label to display the image and add to the right layout
        self.image_label = QLabel("No image selected")  
        right_layout.addWidget(self.image_label)  
        
        #########################################################################################
        # Show the main window
        self.show()  

    #############################################################################################
    # Function for Choosing an excel file
    def browse_file(self):
        # Create a file dialog
        file_dialog = QFileDialog()  
        # Get the file path
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xls *.xlsx)")  
        if file_path:
            # Set the file path in the line edit
            self.file_edit.setText(file_path)  
            # Load the sheets from the file
            self.load_sheets(file_path)  

    #############################################################################################
    # Function for Loading the excel file 
    def load_sheets(self, file_path):
        try:
            # Load all sheets from the Excel file into a dictionary
            self.df_dict = pd.read_excel(file_path, sheet_name=None)  
            self.sheet_combo.clear()  # Clear the combo box
            self.sheet_combo.addItems(self.df_dict.keys())  # Add the sheet names to the combo box
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))  

    #############################################################################################
    # Function for button Clear
    def clear_results(self):
        reply = QMessageBox.question(self, 'Confirm Clear', 'Are you sure you want to clear the results?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.result_table.setRowCount(0)  
            self.file_edit.clear()  
            self.sheet_combo.clear() 
            self.sheet_combo.setVisible(False)  
            self.money_edit.clear()  

    #############################################################################################
    # Function for button Search
    def search_money(self):
        money_amount = self.money_edit.text().strip()  # Get the money amount
        if not money_amount:
            QMessageBox.warning(self, "Input Error", "Please enter a money amount.")  
            return

        current_sheet = self.sheet_combo.currentText()  # Get the current sheet name
        df = self.df_dict[current_sheet]  # Get the DataFrame for the current sheet

        # Filter rows that contain the money amount
        result = df[df.apply(lambda row: row.astype(str).str.contains(money_amount).any(), axis=1)]  
        # Count the number of matching rows
        count = len(result)  

        # Get the current number of rows in the table
        row_position = self.result_table.rowCount() 
        # Insert a new row
        self.result_table.insertRow(row_position)  
        
        # Set the money amount, count, total amount and current sheet name to the table
        self.result_table.setItem(row_position, 0, QTableWidgetItem(money_amount))  
        self.result_table.setItem(row_position, 1, QTableWidgetItem(str(count)))  
        self.result_table.setItem(row_position, 2, QTableWidgetItem(str(count * float(money_amount)))) 
        self.result_table.setItem(row_position, 3, QTableWidgetItem(current_sheet))  

        # Create a layout for the action buttons
        action_layout = QHBoxLayout()  
        
        # Create Send button, connect to send_single_data function and add button to the layout
        send_button = QPushButton("Send") 
        send_button.setFixedHeight(25)  
        send_button.clicked.connect(lambda: self.send_single_data(money_amount, count, count * float(money_amount), current_sheet))  
        action_layout.addWidget(send_button)  
        
        # Create Delete button, connect to confirm_delete_row function and add button to the layout
        delete_button = QPushButton("Delete")  
        delete_button.setFixedHeight(25)  
        delete_button.clicked.connect(lambda: self.confirm_delete_row(row_position))  
        action_layout.addWidget(delete_button)  

        # Create a widget for the action buttons andSet the layout for the action widget
        action_widget = QWidget() 
        action_widget.setLayout(action_layout)  
        
        # Add the action widget to the table
        self.result_table.setCellWidget(row_position, 4, action_widget)  

    #############################################################################################
    # Function for Sending a specific row's data in the table
    def send_single_data(self, money, count, total, sheet_name):
        try:
            # Replace with the client's IP address
            server_ip = '127.0.0.1'  
            server_port = 12345 
            data = {
                'file_path': self.file_edit.text(), 
                'sheet_name': sheet_name,  
                'results': [{'money': money, 'time_repeated': str(count), 'total': str(total), 'sheet_name': sheet_name}]  
            }
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Connect to the server
                s.connect((server_ip, server_port))  
                # Send the data to the server
                s.sendall(json.dumps(data).encode('utf-8'))  
                
            QMessageBox.information(self, "Success", "Data sent to client.") 
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e)) 

    #############################################################################################
    # Function for Sending all data in table
    def send_all_data(self):
        try:
            # Replace with the client's IP address
            server_ip = '127.0.0.1'  
            server_port = 12345  
            data = {
                'file_path': self.file_edit.text(), 
                'sheet_name': self.sheet_combo.currentText(),  
                'results': []
            }
            # Iterate through the rows in the table
            for row in range(self.result_table.rowCount()):  
                money = self.result_table.item(row, 0).text()  # Get the money amount
                time_repeated = self.result_table.item(row, 1).text()  # Get the time repeated
                total = self.result_table.item(row, 2).text()  # Get the total amount
                sheet_name = self.result_table.item(row, 3).text()  # Get the sheet name
                data['results'].append({
                    'money': money,
                    'time_repeated': time_repeated,
                    'total': total,
                    'sheet_name': sheet_name
                })
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Connect to the server
                s.connect((server_ip, server_port))  
                # Send the data to the server
                s.sendall(json.dumps(data).encode('utf-8'))  
                
            QMessageBox.information(self, "Success", "All data sent to client.") 
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e)) 

    #############################################################################################
    #Function for Deleting row in table
    def confirm_delete_row(self, row):
        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this row?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Remove the specified row from the table
            self.result_table.removeRow(row)  

    #############################################################################################
    # Function for Choosing an Image
    def choose_image(self):
        options = QFileDialog.Options()  
        # Open the file dialog to choose an image
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)  
        if file_path:
            # Set the chosen image path
            self.image_path = file_path  
            # Load the image and scale it
            pixmap = QPixmap(file_path).scaled(600, 600, aspectRatioMode=1)  
            # Display the image in the label
            self.image_label.setPixmap(pixmap) 
            
            self.image_label.setText("")  

    #############################################################################################
    # Function for Sending the current Image
    def send_image(self):
        try:
            # Check if an image has been chosen
            if not hasattr(self, 'image_path'):  
                QMessageBox.warning(self, "No Image", "Please choose an image first.")  
                return

            # Replace with the client's IP address
            server_ip = '127.0.0.1'  
            server_port = 12345  
            
            # Open the image file
            with open(self.image_path, "rb") as image_file:  
                # Read the image data
                image_data = image_file.read()  
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Connect to the server
                s.connect((server_ip, server_port))  
                # Send the image data to the server
                s.sendall(image_data)  
                
            QMessageBox.information(self, "Success", "Image sent to client.")  
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e)) 

    #############################################################################################
    # This method is a callback that gets called whenever the file being watched is modified
    def on_modified(self, event):
        # Check if the modified file is the current file
        if event.src_path == self.file_edit.text():  
            # Reload the sheets
            self.load_sheets(self.file_edit.text())  

    #############################################################################################
    # Function for starts watching a specified file for modifications
    def start_watching(self, file_path):
        # Create a file system event handler
        event_handler = FileSystemEventHandler()  
        # Set the on_modified method as the handler for file modifications
        event_handler.on_modified = self.on_modified  
        # Schedule the observer to watch the file path
        self.observer.schedule(event_handler, file_path, recursive=False)  
        self.observer.start()  

    #############################################################################################
    # Function for stops watching the file for modifications
    def stop_watching(self):
        self.observer.stop()  
        # Wait for the observer to finish
        self.observer.join()  

#################################################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv) 
    search_and_count_app = SearchAndCountMoneyRepeatTime()  # Create an instance of the main window
    sys.exit(app.exec_())  # Start the event loop
