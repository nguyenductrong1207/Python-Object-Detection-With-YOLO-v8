from PyQt5 import QtCore, QtWidgets, QtGui

# Screen Resolution 1920 x 1080 and more
class LargeUiDialog(object):
    def setup_ui(self, dialog):
        # Set up the main dialog window with minimize button hint and close buttons
        dialog.setObjectName("UI")
        dialog.setWindowTitle("PNJP Automatic Product Counting Machine")
        dialog.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        dialog.resize(1750, 930)
        dialog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # Load and resize the logo image
        logo_pixmap = QtGui.QPixmap("logo.webp") 
        logo_pixmap = logo_pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo_icon = QtGui.QIcon(logo_pixmap)
        dialog.setWindowIcon(logo_icon)
        
        # Create a text browser for displaying text at the top of the dialog
        self.text_browser = QtWidgets.QTextBrowser(dialog)
        self.text_browser.setGeometry(QtCore.QRect(200, 20, 1200, 60))
        self.text_browser.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.text_browser.setObjectName("TEXT")
        self.text_browser.setStyleSheet("""
            font-weight: bold;
        """)
        self.text_browser.setAlignment(QtCore.Qt.AlignCenter)

        # Create a label to display the total number of objects
        self.total_objects_label = QtWidgets.QLabel(dialog)
        self.total_objects_label.setGeometry(QtCore.QRect(1400, 30, 300, 40))
        self.total_objects_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.total_objects_label.setObjectName("totalObjectsLabel")
        self.total_objects_label.setText("Total Objects: 0")
        self.total_objects_label.setAlignment(QtCore.Qt.AlignCenter)
        self.total_objects_label.setStyleSheet("""
            font-weight: bold;
            font-size: 27px;
            color: red;
        """)
        
        # Create a frame to contain the image labels and other elements
        self.frame_right = QtWidgets.QFrame(dialog)
        self.frame_right.setGeometry(QtCore.QRect(30, 100, 1690, 650))
        self.frame_right.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the frame
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.frame_right.setLineWidth(2) # Set the line width for the frame
        self.frame_right.setObjectName("frameRight")

        # Create a label to display the image
        self.img_label = QtWidgets.QLabel(dialog)
        self.img_label.setGeometry(QtCore.QRect(50, 0, 790, 610))
        self.img_label.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the label
        self.img_label.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.img_label.setLineWidth(6) # Set the line width for the frame
        self.img_label.setAlignment(QtCore.Qt.AlignCenter) # Center the image within the label
        self.img_label.setText("")
        self.img_label.setObjectName("imgLabel")

        # Create a label to display the processed image
        self.processed_img_label = QtWidgets.QLabel(dialog)
        self.processed_img_label.setGeometry(QtCore.QRect(50, 0, 790, 610))
        self.processed_img_label.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the label
        self.processed_img_label.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.processed_img_label.setLineWidth(6) # Set the line width for the frame
        self.processed_img_label.setAlignment(QtCore.Qt.AlignCenter) # Center the image within the label
        self.processed_img_label.setText("")
        self.processed_img_label.setObjectName("processedImgLabel")
        
        # Buttons 
        # Create a QFont object to set the font for buttons
        font = QtGui.QFont()
        
        # Create a button for selecting an Excel file
        self.select_excel_btn = QtWidgets.QPushButton(dialog)
        self.select_excel_btn.setGeometry(QtCore.QRect(30, 770, 140, 50))
        font.setBold(True)
        font.setWeight(75)
        self.select_excel_btn.setFont(font)
        self.select_excel_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.select_excel_btn.setObjectName("Select Excel File")
        self.select_excel_btn.setText("Select Excel")    

        # Create a button for uploading an image
        self.upload_img_btn = QtWidgets.QPushButton(dialog)
        self.upload_img_btn.setGeometry(QtCore.QRect(190, 770, 140, 50))
        font.setBold(True)
        font.setWeight(75)
        self.upload_img_btn.setFont(font)
        self.upload_img_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_img_btn.setObjectName("UPLOAD IMAGE")
        self.upload_img_btn.setText("Upload")
        
        # Create a button for sending data to excel file
        self.send_btn = QtWidgets.QPushButton(dialog)
        self.send_btn.setGeometry(QtCore.QRect(350, 770, 120, 50))
        font.setBold(True)
        font.setWeight(75)
        self.send_btn.setFont(font)
        self.send_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.send_btn.setObjectName("SEND")
        self.send_btn.setText("Send")

        # Create a button for undoing the last action
        self.undo_btn = QtWidgets.QPushButton(dialog)
        self.undo_btn.setGeometry(QtCore.QRect(490, 770, 120, 50))
        font.setBold(True)
        font.setWeight(75)
        self.undo_btn.setFont(font)
        self.undo_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.undo_btn.setObjectName("UNDO")
        self.undo_btn.setText("Undo")
        
        # Create a ComboBox for table selection
        # self.table_select_combo = QtWidgets.QComboBox(dialog)
        # self.table_select_combo.setGeometry(QtCore.QRect(610, 680, 200, 50))
        # font.setBold(True)
        # font.setWeight(75)
        # self.table_select_combo.setFont(font)
        # self.table_select_combo.setObjectName("tableSelectCombo")
        # self.table_select_combo.setCurrentIndex(0)
        
        # Create a button for reloading the application
        self.reload_btn = QtWidgets.QPushButton(dialog)
        self.reload_btn.setGeometry(QtCore.QRect(1460, 770, 120, 50))
        font.setBold(True)
        font.setWeight(75)
        self.reload_btn.setFont(font)
        self.reload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.reload_btn.setObjectName("RELOAD")
        self.reload_btn.setText("Reload")

        # Create a button for quitting the application
        self.quit_btn = QtWidgets.QPushButton(dialog)
        self.quit_btn.setGeometry(QtCore.QRect(1600, 770, 120, 50))
        font.setBold(True)
        font.setWeight(75)
        self.quit_btn.setFont(font)
        self.quit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.quit_btn.setObjectName("QUIT")
        self.quit_btn.setText("Quit")
         
        # Create a combo box for selecting a camera
        self.camera_select_combo = QtWidgets.QComboBox(dialog)
        self.camera_select_combo.setGeometry(QtCore.QRect(675, 840, 120, 60))
        font.setBold(True)
        font.setWeight(75)
        self.camera_select_combo.setFont(font)
        self.camera_select_combo.setObjectName("cameraSelectCombo")
        self.camera_select_combo.setCurrentIndex(0)
        
        # Create a button to connect to the selected camera
        self.camera_btn = QtWidgets.QPushButton(dialog)
        self.camera_btn.setGeometry(QtCore.QRect(800, 840, 150, 60))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.camera_btn.setFont(font)
        self.camera_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.camera_btn.setObjectName("CAMERA")
        self.camera_btn.setText("Connect Camera")

        # Create a button to capture an image from the connected camera
        self.capture_btn = QtWidgets.QPushButton(dialog)
        self.capture_btn.setGeometry(QtCore.QRect(970, 840, 150, 60))
        font.setBold(True)
        font.setWeight(75)
        self.capture_btn.setFont(font)
        self.capture_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.capture_btn.setObjectName("CAPTURE")
        self.capture_btn.setText("Capture")

        QtCore.QMetaObject.connectSlotsByName(dialog)

# Screen Resolution for under 1920 x 1080 
# Scale for 1366 x 768
class SmallUiDialog(object):
    def setup_ui(self, dialog):
        # Set up the main dialog window with minimize button hint and close buttons
        dialog.setObjectName("UI")
        dialog.setWindowTitle("PNJP Automatic Product Counting Machine")
        dialog.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        dialog.resize(1300, 650)
        dialog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # Load and resize the logo image
        logo_pixmap = QtGui.QPixmap("logo.webp") 
        logo_pixmap = logo_pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo_icon = QtGui.QIcon(logo_pixmap)
        dialog.setWindowIcon(logo_icon)
        
        # Create a text browser for displaying text at the top of the dialog
        self.text_browser = QtWidgets.QTextBrowser(dialog)
        self.text_browser.setGeometry(QtCore.QRect(70, 10, 960, 40))
        self.text_browser.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.text_browser.setObjectName("TEXT")
        self.text_browser.setStyleSheet("""
            font-weight: bold;
        """)
        self.text_browser.setAlignment(QtCore.Qt.AlignCenter)

        # Create a label to display the total number of objects
        self.total_objects_label = QtWidgets.QLabel(dialog)
        self.total_objects_label.setGeometry(QtCore.QRect(1000, 10, 300, 40))
        self.total_objects_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.total_objects_label.setObjectName("totalObjectsLabel")
        self.total_objects_label.setText("Total Objects: 0")
        self.total_objects_label.setAlignment(QtCore.Qt.AlignCenter)
        self.total_objects_label.setStyleSheet("""
            font-weight: bold;
            font-size: 22px;
            color: red;
        """)
        
        # Create a frame to contain the image labels and other elements
        self.frame_right = QtWidgets.QFrame(dialog)
        self.frame_right.setGeometry(QtCore.QRect(20, 60, 1260, 440))
        self.frame_right.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the frame
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.frame_right.setLineWidth(1) # Set the line width for the frame
        self.frame_right.setObjectName("frameRight")

        # Create a label to display the image
        self.img_label = QtWidgets.QLabel(dialog)
        self.img_label.setGeometry(QtCore.QRect(50, 0, 550, 500))
        self.img_label.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the label
        self.img_label.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.img_label.setLineWidth(4) # Set the line width for the frame
        self.img_label.setAlignment(QtCore.Qt.AlignCenter) # Center the image within the label
        self.img_label.setText("")
        self.img_label.setObjectName("imgLabel")

        # Create a label to display the processed image
        self.processed_img_label = QtWidgets.QLabel(dialog)
        self.processed_img_label.setGeometry(QtCore.QRect(50, 0, 550, 500))
        self.processed_img_label.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the label
        self.processed_img_label.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.processed_img_label.setLineWidth(4) # Set the line width for the frame
        self.processed_img_label.setAlignment(QtCore.Qt.AlignCenter) # Center the image within the label
        self.processed_img_label.setText("")
        self.processed_img_label.setObjectName("processedImgLabel")
        
        # Buttons 
        # Create a QFont object to set the font for buttons
        font = QtGui.QFont()
        
        # Create a button for selecting an Excel file
        self.select_excel_btn = QtWidgets.QPushButton(dialog)
        self.select_excel_btn.setGeometry(QtCore.QRect(20, 510, 100, 35))
        font.setBold(True)
        font.setWeight(75)
        self.select_excel_btn.setFont(font)
        self.select_excel_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.select_excel_btn.setObjectName("Select Excel File")
        self.select_excel_btn.setText("Select Excel")    

        # Create a button for uploading an image
        self.upload_img_btn = QtWidgets.QPushButton(dialog)
        self.upload_img_btn.setGeometry(QtCore.QRect(135, 510, 100, 35))
        font.setBold(True)
        font.setWeight(75)
        self.upload_img_btn.setFont(font)
        self.upload_img_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_img_btn.setObjectName("UPLOAD IMAGE")
        self.upload_img_btn.setText("Upload")
        
        # Create a button for sending data to excel file
        self.send_btn = QtWidgets.QPushButton(dialog)
        self.send_btn.setGeometry(QtCore.QRect(250, 510, 100, 35))
        font.setBold(True)
        font.setWeight(75)
        self.send_btn.setFont(font)
        self.send_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.send_btn.setObjectName("SEND")
        self.send_btn.setText("Send")

        # Create a button for undoing the last action
        self.undo_btn = QtWidgets.QPushButton(dialog)
        self.undo_btn.setGeometry(QtCore.QRect(365, 510, 100, 35))
        font.setBold(True)
        font.setWeight(75)
        self.undo_btn.setFont(font)
        self.undo_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.undo_btn.setObjectName("UNDO")
        self.undo_btn.setText("Undo")
        
        # Create a button for reloading the application
        self.reload_btn = QtWidgets.QPushButton(dialog)
        self.reload_btn.setGeometry(QtCore.QRect(1065, 510, 100, 35))
        font.setBold(True)
        font.setWeight(75)
        self.reload_btn.setFont(font)
        self.reload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.reload_btn.setObjectName("RELOAD")
        self.reload_btn.setText("Reload")

        # Create a button for quitting the application
        self.quit_btn = QtWidgets.QPushButton(dialog)
        self.quit_btn.setGeometry(QtCore.QRect(1180, 510, 100, 35))
        font.setBold(True)
        font.setWeight(75)
        self.quit_btn.setFont(font)
        self.quit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.quit_btn.setObjectName("QUIT")
        self.quit_btn.setText("Quit")
         
        # Create a combo box for selecting a camera
        self.camera_select_combo = QtWidgets.QComboBox(dialog)
        self.camera_select_combo.setGeometry(QtCore.QRect(450, 570, 120, 40))
        font.setBold(True)
        font.setWeight(75)
        self.camera_select_combo.setFont(font)
        self.camera_select_combo.setObjectName("cameraSelectCombo")
        self.camera_select_combo.setCurrentIndex(0)
        
        # Create a button to connect to the selected camera
        self.camera_btn = QtWidgets.QPushButton(dialog)
        self.camera_btn.setGeometry(QtCore.QRect(575, 570, 150, 40))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.camera_btn.setFont(font)
        self.camera_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.camera_btn.setObjectName("CAMERA")
        self.camera_btn.setText("Connect Camera")

        # Create a button to capture an image from the connected camera
        self.capture_btn = QtWidgets.QPushButton(dialog)
        self.capture_btn.setGeometry(QtCore.QRect(740, 570, 150, 40))
        font.setBold(True)
        font.setWeight(75)
        self.capture_btn.setFont(font)
        self.capture_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.capture_btn.setObjectName("CAPTURE")
        self.capture_btn.setText("Capture")

        QtCore.QMetaObject.connectSlotsByName(dialog)
         