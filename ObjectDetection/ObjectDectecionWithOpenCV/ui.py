from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDesktopWidget 

class UiDialog(object):
    def setup_ui(self, dialog):
        # Set up the main dialog window with minimize button hint and close buttons
        dialog.setObjectName("UI")
        dialog.setWindowTitle("PNJP Automatic Product Counting Machine")
        dialog.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        
        dialog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        # Get screen resolution
        screen_resolution = QDesktopWidget().screenGeometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()
        
        # Choose the UI based on screen resolution
        if screen_width >= 1920 and screen_height >= 1080:
            print("UI Screen Resolution 1920 x 1080 and more")
            # Set Dialog Width and Height
            screenWidth = 1750
            screenHeight = 930
            dialog.resize(screenWidth, screenHeight)
                
            # Set Defaulf Geometry for frame_right, img_label, processed_img_label
            line2X = 30    
            line2Y = 100   
            line2W = 790  
            line2H = 650
                
            # Set Defaulf Geometry for select_excel_btn, upload_img_btn, send_btn, undo_btn, reload_btn, quit_btn
            line3X = 30
            line3Y = 770
            line3W = 120
            line3H = 50
                
            # Set Defaulf Geometry for camera_select_combo, camera_btn, capture_btn
            line4X = 0
            line4Y = 840
            line4W = 150
            line4H = 60  
                
            # Set Margin Line 3 and 4
            margin = 20
            
            # Set Line height for frame_right, img_label, processed_img_label
            frameLineHeight = 2
            imgLineHeight = 6

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
            
        else:
            # Screen Resolution for under 1920 x 1080 
            # Scale for 1366 x 768
            print("UI Screen Resolution 1366 x 768")
            # Set Dialog Width and Height
            screenWidth = 1300
            screenHeight = 650
            dialog.resize(screenWidth, screenHeight)
                    
            # Set Defaulf Geometry for frame_right, img_label, processed_img_label
            line2X = 20    
            line2Y = 60   
            line2W = 600  
            line2H = 440
                    
            # Set Defaulf Geometry for select_excel_btn, upload_img_btn, send_btn, undo_btn, reload_btn, quit_btn
            line3X = 20
            line3Y = 510
            line3W = 100
            line3H = 35
                    
            # Set Defaulf Geometry for camera_select_combo, camera_btn, capture_btn
            line4X = 840
            line4Y = 570
            line4W = 150
            line4H = 40  
                    
            # Set Margin Line 3 and 4
            margin = 15
            
            # Set Line height for frame_right, img_label, processed_img_label
            frameLineHeight = 1
            imgLineHeight = 4
            
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
            
        # Load and resize the logo image
        logo_pixmap = QtGui.QPixmap("logo.webp") 
        logo_pixmap = logo_pixmap.scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo_icon = QtGui.QIcon(logo_pixmap)
        dialog.setWindowIcon(logo_icon)
                   
        # Create a frame to contain the image labels and other elements
        self.frame_right = QtWidgets.QFrame(dialog)
        self.frame_right.setGeometry(QtCore.QRect(line2X, line2Y, screenWidth - (line2X * 2), line2H))
        self.frame_right.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the frame
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.frame_right.setLineWidth(frameLineHeight) # Set the line width for the frame
        self.frame_right.setObjectName("frameRight")

        # Create a label to display the image
        self.img_label = QtWidgets.QLabel(dialog)
        self.img_label.setGeometry(QtCore.QRect(line2X + 20, line2Y, line2W, line2H))
        self.img_label.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the label
        self.img_label.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.img_label.setLineWidth(imgLineHeight) # Set the line width for the frame
        self.img_label.setAlignment(QtCore.Qt.AlignCenter) # Center the image within the label
        self.img_label.setText("")
        self.img_label.setObjectName("imgLabel")

        # Create a label to display the processed image
        self.processed_img_label = QtWidgets.QLabel(dialog)
        self.processed_img_label.setGeometry(QtCore.QRect(line2X + 20, line2Y, line2W, line2H))
        self.processed_img_label.setFrameShape(QtWidgets.QFrame.Box) # Add a box frame around the label
        self.processed_img_label.setFrameShadow(QtWidgets.QFrame.Raised) # Apply a raised shadow effect
        self.processed_img_label.setLineWidth(imgLineHeight) # Set the line width for the frame
        self.processed_img_label.setAlignment(QtCore.Qt.AlignCenter) # Center the image within the label
        self.processed_img_label.setText("")
        self.processed_img_label.setObjectName("processedImgLabel")
        
        # Buttons 
        # Create a QFont object to set the font for buttons
        font = QtGui.QFont()
        
        # Create a button for selecting an Excel file
        self.select_excel_btn = QtWidgets.QPushButton(dialog)
        self.select_excel_btn.setGeometry(QtCore.QRect(line3X, line3Y, line3W, line3H))
        font.setBold(True)
        font.setWeight(75)
        self.select_excel_btn.setFont(font)
        self.select_excel_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.select_excel_btn.setObjectName("Select Excel File")
        self.select_excel_btn.setText("Select Excel")    

        # Create a button for uploading an image
        self.upload_img_btn = QtWidgets.QPushButton(dialog)
        self.upload_img_btn.setGeometry(QtCore.QRect(line3X + line3W + margin, line3Y, line3W, line3H))
        font.setBold(True)
        font.setWeight(75)
        self.upload_img_btn.setFont(font)
        self.upload_img_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_img_btn.setObjectName("UPLOAD IMAGE")
        self.upload_img_btn.setText("Upload")
        
        # Create a button for sending data to excel file
        self.send_btn = QtWidgets.QPushButton(dialog)
        self.send_btn.setGeometry(QtCore.QRect(line3X + (line3W + margin) * 2, line3Y, line3W, line3H))
        font.setBold(True)
        font.setWeight(75)
        self.send_btn.setFont(font)
        self.send_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.send_btn.setObjectName("SEND")
        self.send_btn.setText("Send")

        # Create a button for undoing the last action
        self.undo_btn = QtWidgets.QPushButton(dialog)
        self.undo_btn.setGeometry(QtCore.QRect(line3X + (line3W + margin) * 3, line3Y, line3W, line3H))
        font.setBold(True)
        font.setWeight(75)
        self.undo_btn.setFont(font)
        self.undo_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.undo_btn.setObjectName("UNDO")
        self.undo_btn.setText("Undo")
        
        # Create a button for reloading the application
        self.reload_btn = QtWidgets.QPushButton(dialog)
        self.reload_btn.setGeometry(QtCore.QRect(screenWidth - line3X - line3W * 2 - margin, line3Y, line3W, line3H))
        font.setBold(True)
        font.setWeight(75)
        self.reload_btn.setFont(font)
        self.reload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.reload_btn.setObjectName("RELOAD")
        self.reload_btn.setText("Reload")

        # Create a button for quitting the application
        self.quit_btn = QtWidgets.QPushButton(dialog)
        self.quit_btn.setGeometry(QtCore.QRect(screenWidth - line3X - line3W, line3Y, line3W, line3H))
        font.setBold(True)
        font.setWeight(75)
        self.quit_btn.setFont(font)
        self.quit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.quit_btn.setObjectName("QUIT")
        self.quit_btn.setText("Quit")
         
        # Create a combo box for selecting a camera
        self.camera_select_combo = QtWidgets.QComboBox(dialog)
        self.camera_select_combo.setGeometry(QtCore.QRect(int(screenWidth / 2 - line4W / 2) - 5 - line4W + 30, line4Y, line4W - 30, line4H))
        font.setBold(True)
        font.setWeight(75)
        self.camera_select_combo.setFont(font)
        self.camera_select_combo.setObjectName("cameraSelectCombo")
        self.camera_select_combo.setCurrentIndex(0)
        
        # Create a button to connect to the selected camera
        self.camera_btn = QtWidgets.QPushButton(dialog)
        self.camera_btn.setGeometry(QtCore.QRect(int(screenWidth / 2 - line4W / 2), line4Y, line4W, line4H))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.camera_btn.setFont(font)
        self.camera_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.camera_btn.setObjectName("CAMERA")
        self.camera_btn.setText("Connect Camera")

        # Create a button to capture an image from the connected camera
        self.capture_btn = QtWidgets.QPushButton(dialog)
        self.capture_btn.setGeometry(QtCore.QRect(int(screenWidth / 2 - line4W / 2) + line4W + margin, line4Y, line4W, line4H))
        font.setBold(True)
        font.setWeight(75)
        self.capture_btn.setFont(font)
        self.capture_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.capture_btn.setObjectName("CAPTURE")
        self.capture_btn.setText("Capture")

        QtCore.QMetaObject.connectSlotsByName(dialog)
