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

    def init_ui(self):
        self.setWindowTitle("TÌM BẢNG MÔ TẢ (Threaded)")
        self.setFixedSize(450, 250)  # Optional: Set a fixed window size

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create label and line edit
        self.filename_label = QLabel("Enter filename (wildcards allowed):")
        self.filename_edit = QLineEdit()
        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_edit)
        self.filename_edit.setText("")
        
        # Create button and connect to search function
        self.search_button = QPushButton("Search")
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
        
        # Show the window
        self.show()

    def search_files(self):
        search_pattern = self.filename_edit.text()

        # Validate input (optional)
        if not search_pattern:
            QMessageBox.warning(self, "Warning", "Please enter a filename or ID to search.")
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

root_path = 'H:\QUANLYHETHONG'  # Change this to the path of your folder
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSearchWindow()
    sys.exit(app.exec_())
