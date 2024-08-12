from PyQt5 import QtCore, QtWidgets, QtGui

class UiDialog(object):
    def setup_ui(self, dialog):
        dialog.setObjectName("Dialog")
        dialog.setWindowTitle("Dialog")
        dialog.resize(1460, 850)
        dialog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        # Create a horizontal layout for text_browser and total_objects_label
        self.text_browser = QtWidgets.QTextBrowser(dialog)
        self.text_browser.setGeometry(QtCore.QRect(190, 30, 900, 60))
        self.text_browser.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.text_browser.setObjectName("TEXT")
        self.text_browser.setStyleSheet("""
            font-weight: bold;
        """)
        self.text_browser.setAlignment(QtCore.Qt.AlignCenter)

        self.total_objects_label = QtWidgets.QLabel(dialog)
        self.total_objects_label.setGeometry(QtCore.QRect(1100, 40, 300, 40))
        self.total_objects_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.total_objects_label.setObjectName("totalObjectsLabel")
        self.total_objects_label.setText("Total Objects: 0")
        self.total_objects_label.setAlignment(QtCore.Qt.AlignCenter)
        self.total_objects_label.setStyleSheet("""
            font-weight: bold;
            font-size: 27px;
            color: red;
        """)

        self.img_label = QtWidgets.QLabel(dialog)
        self.img_label.setGeometry(QtCore.QRect(50, 0, 680, 255))
        self.img_label.setFrameShape(QtWidgets.QFrame.Box)
        self.img_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.img_label.setLineWidth(6)
        self.img_label.setText("")
        self.img_label.setObjectName("imgLabel")

        self.processed_img_label = QtWidgets.QLabel(dialog)
        self.processed_img_label.setGeometry(QtCore.QRect(50, 0, 680, 255))
        self.processed_img_label.setFrameShape(QtWidgets.QFrame.Box)
        self.processed_img_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.processed_img_label.setLineWidth(6)
        self.processed_img_label.setText("")
        self.processed_img_label.setObjectName("processedImgLabel")

        self.frame_right = QtWidgets.QFrame(dialog)
        self.frame_right.setGeometry(QtCore.QRect(30, 100, 1400, 550))
        self.frame_right.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_right.setLineWidth(2)
        self.frame_right.setObjectName("frameRight")
        
        # Buttons
        font = QtGui.QFont()
        
        self.select_excel_btn = QtWidgets.QPushButton(dialog)
        self.select_excel_btn.setGeometry(QtCore.QRect(30, 680, 140, 50))
        font.setBold(True)
        font.setWeight(75)
        self.select_excel_btn.setFont(font)
        self.select_excel_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.select_excel_btn.setObjectName("Select Excel File")
        self.select_excel_btn.setText("Select Excel File")    

        self.upload_btn = QtWidgets.QPushButton(dialog)
        self.upload_btn.setGeometry(QtCore.QRect(190, 680, 140, 50))
        font.setBold(True)
        font.setWeight(75)
        self.upload_btn.setFont(font)
        self.upload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_btn.setObjectName("UPLOAD IMAGE")
        self.upload_btn.setText("Upload Image")
        
        self.send_btn = QtWidgets.QPushButton(dialog)
        self.send_btn.setGeometry(QtCore.QRect(350, 680, 110, 50))
        font.setBold(True)
        font.setWeight(75)
        self.send_btn.setFont(font)
        self.send_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.send_btn.setObjectName("SEND")
        self.send_btn.setText("Send")

        self.undo_btn = QtWidgets.QPushButton(dialog)
        self.undo_btn.setGeometry(QtCore.QRect(480, 680, 110, 50))
        font.setBold(True)
        font.setWeight(75)
        self.undo_btn.setFont(font)
        self.undo_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.undo_btn.setObjectName("UNDO")
        self.undo_btn.setText("Undo")
        
        self.reload_btn = QtWidgets.QPushButton(dialog)
        self.reload_btn.setGeometry(QtCore.QRect(1190, 680, 110, 50))
        font.setBold(True)
        font.setWeight(75)
        self.reload_btn.setFont(font)
        self.reload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.reload_btn.setObjectName("RELOAD")
        self.reload_btn.setText("Reload")

        self.quit_btn = QtWidgets.QPushButton(dialog)
        self.quit_btn.setGeometry(QtCore.QRect(1320, 680, 110, 50))
        font.setBold(True)
        font.setWeight(75)
        self.quit_btn.setFont(font)
        self.quit_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.quit_btn.setObjectName("QUIT")
        self.quit_btn.setText("Quit")
        
        # Add a ComboBox for camera selection
        self.camera_select_combo = QtWidgets.QComboBox(dialog)
        self.camera_select_combo.setGeometry(QtCore.QRect(537, 760, 110, 60))
        font.setBold(True)
        font.setWeight(75)
        self.camera_select_combo.setFont(font)
        self.camera_select_combo.setObjectName("cameraSelectCombo")
        # self.camera_select_combo.addItems(["Camera 0", "Camera 1", "Camera 2", "Camera 3"])
        self.camera_select_combo.setCurrentIndex(0)
        
        self.camera_btn = QtWidgets.QPushButton(dialog)
        self.camera_btn.setGeometry(QtCore.QRect(650, 760, 140, 60))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.camera_btn.setFont(font)
        self.camera_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.camera_btn.setObjectName("CAMERA")
        self.camera_btn.setText("Connect Camera")

        self.capture_btn = QtWidgets.QPushButton(dialog)
        self.capture_btn.setGeometry(QtCore.QRect(810, 760, 110, 60))
        font.setBold(True)
        font.setWeight(75)
        self.capture_btn.setFont(font)
        self.capture_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.capture_btn.setObjectName("CAPTURE")
        self.capture_btn.setText("Capture")

        QtCore.QMetaObject.connectSlotsByName(dialog)