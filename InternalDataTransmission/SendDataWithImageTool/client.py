import sys
import socket
import threading
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSplitter, QMessageBox
)
from PyQt5.QtGui import QPixmap

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui() 
        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)  
        self.server_thread.start()

    def init_ui(self):
        self.setWindowTitle("Client View")  
        self.setFixedSize(1400, 600)  

        central_widget = QWidget()  # Create the central widget
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)  # Set a horizontal layout for the central widget ( by default )

        splitter = QSplitter()  # Create a splitter to divide the UI into 2 parts
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
        
        # Create a layout for the file path 
        self.file_layout = QHBoxLayout()  
        self.file_label = QLabel("Excel file path:") 
        self.file_edit = QLineEdit()  
        
        self.file_edit.setReadOnly(True)
        self.file_edit.setFixedHeight(35)  
        
        # Add the file label, file edit to the file layout
        self.file_layout.addWidget(self.file_label) 
        self.file_layout.addWidget(self.file_edit)  
        
        # Add the file layout to the left layout
        left_layout.addLayout(self.file_layout)  
        
        #########################################################################################

        # Create a layout for the sheet name and money amount
        self.sheet_layout = QHBoxLayout()  
        self.sheet_label = QLabel("Sheet name:") 
        self.sheet_combo = QComboBox() 
        
        self.sheet_combo.setEnabled(False) 
        self.sheet_combo.setFixedWidth(240) 
        self.sheet_combo.setFixedHeight(35) 
        
        # Add the sheet label, sheet combobox to the layout
        self.sheet_layout.addWidget(self.sheet_label)  
        self.sheet_layout.addWidget(self.sheet_combo)  
        
        # Add the sheet layout to the left layout
        left_layout.addLayout(self.sheet_layout)  
        
        #########################################################################################

         # Create a received data label and add to the left layout
        self.label = QLabel("Received Data:") 
        left_layout.addWidget(self.label)  
        
        #########################################################################################

        # Create a table widget for displaying the results and add to the left layout
        self.result_table = QTableWidget()  
        left_layout.addWidget(self.result_table) 
        
        #########################################################################################

        # Create a widget for the right part - Image Display
        right_widget = QWidget() 
        right_widget.setFixedWidth(700)  
        
        # Set a layout for the right widget
        right_layout = QVBoxLayout(right_widget)  
        
        # Add the right widget to the splitter
        splitter.addWidget(right_widget)  
        
        #########################################################################################

        # Create label for image and add to the right layout
        self.image_label_title = QLabel("Image Sent") 
        right_layout.addWidget(self.image_label_title)  
        
        # Create label to display the image and add to the right layout
        self.image_label = QLabel("No image received")  
        right_layout.addWidget(self.image_label) 

        #########################################################################################
        # Show the main window
        self.show()  
    
    #############################################################################################
    # Function for continuously listens for incoming connections, receives data from connected clients, 
    # and processes the data to either display it as JSON in a table or as an image
    def start_server(self):
        # Replace with the server's IP address
        server_ip = '127.0.0.1'  
        server_port = 12345  
        
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        # Bind the socket to the address and port
        server_socket.bind((server_ip, server_port))  
        # Listen for incoming connections
        server_socket.listen(1)  

        while True:
            try:
                # Accepting Connections and Receiving Data
                # Accept a new connection
                client_socket, _ = server_socket.accept()  
                data = b''
                while True:
                    # Receive data in chunks
                    part = client_socket.recv(1024)  
                    if not part:
                        break
                    data += part
                
                # Processing the Received Data    
                # Check if the data is JSON
                if data.startswith(b'{'):  
                    # Display the JSON data
                    self.display_data(data)  
                else:
                    # Display the image data
                    self.display_image(data)  
                # Close the client socket
                client_socket.close()  
                
            except Exception as e:
                QMessageBox.critical(self, "Error in Server: ", str(e)) 

    #############################################################################################
    # Function for Displaying the Getting Data
    def display_data(self, data):
        try:
            # Decode and load the JSON data
            data = json.loads(data.decode('utf-8'))  
            # Set the file path in the line edit
            self.file_edit.setText(data['file_path'])  
            
            # Clear, Add the sheet name to the combo box and Set the current text of the combo box
            self.sheet_combo.clear()  
            self.sheet_combo.addItem(data['sheet_name'])   
            self.sheet_combo.setCurrentText(data['sheet_name']) 

            # Clear previous data in the table before display new data
            self.result_table.setRowCount(0)  
            
            # Set the number of columns in the table
            self.result_table.setColumnCount(4)  
            # Set the column headers
            self.result_table.setHorizontalHeaderLabels(["Money", "Time Repeated", "Total", "Sheet Name"])  

            # Iterate through the results
            for result in data['results']:  
                # Get the current number of rows in the table
                row_position = self.result_table.rowCount()  
                # Insert a new row
                self.result_table.insertRow(row_position)  
                
                # Set the money amount, time repeated, total amount and current sheet name to the table
                self.result_table.setItem(row_position, 0, QTableWidgetItem(result['money']))  
                self.result_table.setItem(row_position, 1, QTableWidgetItem(result['time_repeated']))  
                self.result_table.setItem(row_position, 2, QTableWidgetItem(result['total']))
                self.result_table.setItem(row_position, 3, QTableWidgetItem(result['sheet_name']))  

            # Make the table read-only
            self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)  
            
        except Exception as e:
            QMessageBox.critical(self, "Error displaying data: ", str(e)) 

    #############################################################################################
    # Function for Displaying the Getting Image
    def display_image(self, data):
        try:
            # Open a file to write the image data
            with open("received_image.png", "wb") as file:  
                # Write the image data to the file
                file.write(data)  
            # Load and scale the image
            pixmap = QPixmap("received_image.png").scaled(600, 600, aspectRatioMode=1)  
            # Display the image in the label
            self.image_label.setPixmap(pixmap)  
            # Clear the text "No image selected" in the label
            self.image_label.setText("") 
            
        except Exception as e:
            QMessageBox.critical(self, "Error displaying image: ", str(e)) 
            
#################################################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)  
    client_app = ClientApp()  # Create an instance of the main window
    sys.exit(app.exec_())  # Start the event loop
