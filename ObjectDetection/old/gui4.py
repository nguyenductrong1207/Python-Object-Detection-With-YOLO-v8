import sys, os, subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from glob import glob  # For filename searching


class FileSearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    #def init_ui(self):
     #   self.setWindowTitle("TÌM BẢNG MÔ TẢ MBT (Threaded)")
      #  self.setFixedSize(350, 350)  # Optional: Set a fixed window size
        class MyWindow(QWidget):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("TÌM BẢNG MÔ TẢ MBT (Threaded)")
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create label and line edit
        self.filename_labelLSX_ID = QLabel("Auto Enter LSX_ID:")
        self.filename_editLSX_ID = QLineEdit()
        layout.addWidget(self.filename_labelLSX_ID)
        layout.addWidget(self.filename_editLSX_ID)
        self.filename_editLSX_ID.setText(" ")
        
        # Create button and connect to search function
        self.search_buttonID = QPushButton("Tim BMT_ID")
        self.search_buttonID.clicked.connect(self.search_id)
        layout.addWidget(self.search_buttonID)
        
        # Create label and line edit
        self.filename_label = QLabel("Enter BMT ID")
        self.filename_edit = QLineEdit()
        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_edit)
        #self.filename_edit.setText("ABC")
        
        # Create button and connect to search function
        self.search_button = QPushButton("Search FILE BMT")
        self.search_button.clicked.connect(self.search_files)
        layout.addWidget(self.search_button)

        # Create a progress label (optional)
        self.progress_label = QLabel("Searching...")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Create label and New Field
        self.filename_labelLSX = QLabel("Mã Lệnh sản xuất (LSX):")
        self.filename_editLSX = QLineEdit()
        layout.addWidget(self.filename_labelLSX)
        layout.addWidget(self.filename_editLSX)
        
        # Create label and line edit
        self.filename_labelMBT = QLabel("Mã Bảng mô tả (BMT):")
        self.filename_editMBT = QLineEdit()
        layout.addWidget(self.filename_labelMBT)
        layout.addWidget(self.filename_editMBT)

        # Create label and line edit
        self.filename_labelMBT1 = QLabel("Mã 1 Bảng mô tả (BMT):")
        self.filename_editMBT1 = QLineEdit()
        layout.addWidget(self.filename_labelMBT1)
        layout.addWidget(self.filename_editMBT1)
        
        #set focus
        #self.filename_editMBT.setFocus()
        #self.filename_editMBT.setText("XYZ")
        #self.filename_editMBT.selectAll()
        
        # Show the window
        self.show()
        self.search_button.setEnabled(False)
        self.search_button.setVisible(False)

    ############################
    def search_id(self):
        search_ID = self.filename_editLSX_ID.text()

        print("search_ID",search_ID)

        # Validate input (optional)
        if not search_ID:
            QMessageBox.warning(self, "Warning", "Please enter a filename or ID to search!!!")
            return

        # Disable search button and show progress label (optional)
        self.search_buttonID.setEnabled(False)
        self.progress_label.setVisible(True)

        # Create and start a thread for searching
        search_thread = threading.Thread(target=get_data_by_lsx_id, args=(excel_file,str(search_ID)))
        search_thread.start()

        # Get du lieu chi 1 dong duy nhat , dung voi LSX ID cung cap
        data_row = get_data_by_lsx_id(excel_file, str(search_ID))

        if search_thread is not None:
            print("Found data:")
            # Access data from the row using column names (e.g., data_row['BMT_ID'])
            print(data_row)
            bmt_id = data_row['BMT_ID']
            cat_id = data_row['Catalogue']
            self.filename_editLSX.setText(search_ID)
            self.filename_editMBT.setText(bmt_id)
            self.filename_editMBT1.setText(cat_id)
        else:
            print("No data found for LSX_ID:", lsx_id_to_find)
    ###############################

        # Re-enable search button and hide progress label (optional)
        self.search_buttonID.setEnabled(True)
        self.progress_label.setVisible(False)

        ########## 2 trong 1
        self.filename_edit.setText(bmt_id)
        self.search_files()
        
    def search_files(self):
        search_pattern = self.filename_edit.text()
        
        #print("Bien nhan input",search_pattern)
        #self.print2cosole()
        
        # Validate input (optional)
        if not search_pattern:
            QMessageBox.warning(self, "Warning", "Please enter a filename or ID to search!!!")
            return

        # Disable search button and show progress label (optional)
        self.search_button.setEnabled(False)
        self.progress_label.setVisible(True)

        # Create and start a thread for searching
        search_thread = threading.Thread(target=self.threaded_search, args=(search_pattern,))
        search_thread.start()

    def threaded_search(self, search_pattern):
        # Search using glob and store results
        #found_files = glob(search_pattern)
        found_files = self.open_image_by_id(root_path,search_pattern)
        

        # Re-enable search button and hide progress label (optional)
        self.search_button.setEnabled(True)
        self.progress_label.setVisible(False)

        # Display search results in the main thread (using Qt mechanism)
        self.display_search_results(found_files)

    def display_search_results(self, found_files):
        self.progress_label.setVisible(True)
        if found_files:
            #message = "Found files:\n" + "\n".join(found_files)
            message = "Found " + str(found_files)
            #QMessageBox.information(self, "Search Results", message)
            self.progress_label.setText(message)
        else:
            #QMessageBox.information(self, "Search Results", "No files found matching the pattern.")
            self.progress_label.setText("No files found matching the pattern")

    def open_image_by_id(self, root_path, file_id):
        print("dang tim kiem... ")
        # Walk through directory and subdirectories
        for dirpath, dirnames, filenames in os.walk(root_path):
            print(".", end="")
            for filename in filenames:
                # Check for common image file extensions
                if filename.startswith(file_id) and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(dirpath, filename)
                    # Properly format the path to handle spaces
                    formatted_path = f'"{file_path}"'
                    # Open the image file using the default application
                    subprocess.run(f'start "" {formatted_path}', shell=True)
                    #print("Image opened successfully:", file_path)
                    #input("\n>>>>>>>>>>> \n Cam on da su dung chuong trinh!")
                    #print(">>>>>>>>>>>>>")
                    #print("Enter to exist")
                    return file_path
        print("Image not found.")
        return False

    def print2cosole(self):
        print("Print ra man hinh")

    def init_ui(self):
        pass


root_path = 'H:\QUANLYHETHONG'  # Change this to the path of your folder

import pandas as pd

def get_data_by_lsx_id(excel_filepath, lsx_id):
  """
  This function opens an Excel file, reads the data into a DataFrame,
  and returns the row where the LSX_ID matches the provided lsx_id.

  Args:
      excel_filepath (str): Path to the Excel file.
      lsx_id (str): The LSX_ID value to search for.

  Returns:
      pandas.DataFrame: A DataFrame containing the row with the matching LSX_ID,
                        or None if no match is found.
  """
  try:
    # Read the Excel data into a DataFrame
    df = pd.read_excel(excel_filepath)

    # Select the row where LSX_ID matches the provided lsx_id
    filtered_df = df[df['LSX_ID'] == lsx_id]

    # Check if there's a match
    if filtered_df.empty:
      return None
    else:
      # Return the first row (assuming unique LSX_ID)
      return filtered_df.iloc[0]

  except FileNotFoundError:
    print(f"Error: Excel file not found at {excel_filepath}")
    return None
  except pd.errors.ParserError:
    print(f"Error: Could not parse Excel file at {excel_filepath}")
    return None

# Example usage
excel_file = "C:\\Users\\duy.lt\\Documents\\csdl.xlsx" # Replace with your actual file path
lsx_id_to_find = "101622253"
#data_row = get_data_by_lsx_id(excel_file, lsx_id_to_find)
def search_id(self):
    search_ID = self.filename_editLSX_ID.text()

    print("search_ID", search_ID)

    # Validate input (optional)
    if not search_ID:
        QMessageBox.warning(self, "Warning", "Please enter a filename or ID to search!!!")
        return

    # Disable search button and show progress label (optional)
    self.search_buttonID.setEnabled(False)
    self.progress_label.setVisible(True)

    # Create and start a thread for searching
    search_thread = threading.Thread(target=get_data_by_lsx_id, args=(excel_file, str(search_ID)))
    search_thread.start()

    # Wait for the thread to finish
    search_thread.join()

    # Get du lieu chi 1 dong duy nhat , dung voi LSX ID cung cap
    data_row = get_data_by_lsx_id(excel_file, str(search_ID))

    if data_row is not None:
        print("Found data:")
        # Access data from the row using column names (e.g., data_row['BMT_ID'])
        print(data_row)
        bmt_id = data_row['BMT_ID']
        cat_id = data_row['Catalogue']
        self.filename_editLSX.setText(search_ID)
        self.filename_editMBT.setText(bmt_id)
        self.filename_editMBT1.setText(cat_id)

        # Re-enable search button and hide progress label (optional)
        self.search_buttonID.setEnabled(True)
        self.progress_label.setVisible(False)

        # Set BMT_ID to search and trigger file search
        self.filename_edit.setText(bmt_id)
        self.search_files()
    else:
        print("No data found for LSX_ID:", search_ID)
        # Re-enable search button and hide progress label (optional)
        self.search_buttonID.setEnabled(True)
        self.progress_label.setVisible(False)
if __name__ != "__main__":
    pass
else:
    app = QApplication(sys.argv)
    window = FileSearchWindow()
    sys.exit(app.exec_())
