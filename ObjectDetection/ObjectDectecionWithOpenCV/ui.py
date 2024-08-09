from PyQt5 import QtCore, QtWidgets, QtGui

class UiDialog(object):
    def setup_ui(self, dialog):
        dialog.setObjectName("Dialog")
        dialog.resize(1500, 800)
        dialog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        # Create a horizontal layout for text_browser and total_objects_label
        self.horizontal_layout_widget = QtWidgets.QWidget(dialog)
        self.horizontal_layout_widget.setGeometry(QtCore.QRect(410, 30, 1000, 41))
        self.horizontal_layout_widget.setObjectName("horizontalLayoutWidget")

        self.horizontal_layout = QtWidgets.QHBoxLayout(self.horizontal_layout_widget)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setSpacing(270)  # Add more space between text_browser and total_objects_label
        self.horizontal_layout.setObjectName("horizontalLayout")

        self.text_browser = QtWidgets.QTextBrowser(self.horizontal_layout_widget)
        self.text_browser.setObjectName("TEXT")
        self.horizontal_layout.addWidget(self.text_browser)

        self.total_objects_label = QtWidgets.QLabel(self.horizontal_layout_widget)
        self.total_objects_label.setObjectName("totalObjectsLabel")
        self.total_objects_label.setAlignment(QtCore.Qt.AlignCenter)
        self.total_objects_label.setStyleSheet("""
            font-weight: bold;
            font-size: 27px;
            color: red;
        """)
        self.horizontal_layout.addWidget(self.total_objects_label)

        self.img_label = QtWidgets.QLabel(dialog)
        self.img_label.setGeometry(QtCore.QRect(49, 0, 800, 700))
        self.img_label.setFrameShape(QtWidgets.QFrame.Box)
        self.img_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.img_label.setLineWidth(6)
        self.img_label.setText("")
        self.img_label.setObjectName("imgLabel")

        self.processed_img_label = QtWidgets.QLabel(dialog)
        self.processed_img_label.setGeometry(QtCore.QRect(49, 0, 1000, 1000))
        self.processed_img_label.setFrameShape(QtWidgets.QFrame.Box)
        self.processed_img_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.processed_img_label.setLineWidth(6)
        self.processed_img_label.setText("")
        self.processed_img_label.setObjectName("processedImgLabel")

        self.frame_right = QtWidgets.QFrame(dialog)
        self.frame_right.setGeometry(QtCore.QRect(37, 77, 1400, 550))
        self.frame_right.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_right.setObjectName("frameRight")

        self.camera_btn = QtWidgets.QPushButton(dialog)
        self.camera_btn.setGeometry(QtCore.QRect(30, 670, 111, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.camera_btn.setFont(font)
        self.camera_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.camera_btn.setObjectName("CAMERA")

        self.capture_btn = QtWidgets.QPushButton(dialog)
        self.capture_btn.setGeometry(QtCore.QRect(680, 710, 120, 55))
        font.setBold(True)
        font.setWeight(75)
        self.capture_btn.setFont(font)
        self.capture_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.capture_btn.setObjectName("CAPTURE")

        self.undo_btn = QtWidgets.QPushButton(dialog)
        self.undo_btn.setGeometry(QtCore.QRect(320, 670, 111, 51))
        font.setBold(True)
        font.setWeight(75)
        self.undo_btn.setFont(font)
        self.undo_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.undo_btn.setObjectName("UNDO")

        self.upload_btn = QtWidgets.QPushButton(dialog)
        self.upload_btn.setGeometry(QtCore.QRect(170, 670, 111, 51))
        font.setBold(True)
        font.setWeight(75)
        self.upload_btn.setFont(font)
        self.upload_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.upload_btn.setObjectName("UPLOAD")

        self.quit_btn = QtWidgets.QPushButton(dialog)
        self.quit_btn.setGeometry(QtCore.QRect(1330, 660, 93, 28))
        self.quit_btn.setPalette(self.get_palette())
        self.quit_btn.setObjectName("QUIT")

        self.send_btn = QtWidgets.QPushButton(dialog)
        self.send_btn.setGeometry(QtCore.QRect(480, 670, 111, 51))
        font.setBold(True)
        font.setWeight(75)
        self.send_btn.setFont(font)
        self.send_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.send_btn.setObjectName("SEND")

        self.retranslate_ui(dialog)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def get_palette(self):
        palette = QtGui.QPalette()
        
        # Button color
        brush = QtGui.QBrush(QtGui.QColor(240, 2, 2))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)

        # Text color
        brush = QtGui.QBrush(QtGui.QColor(255, 248, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)

        # Disabled text color
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)

        return palette

    def retranslate_ui(self, dialog):
        _translate = QtCore.QCoreApplication.translate
        dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.camera_btn.setText(_translate("Dialog", "Camera"))
        self.capture_btn.setText(_translate("Dialog", "Capture"))
        self.undo_btn.setText(_translate("Dialog", "Undo"))
        self.upload_btn.setText(_translate("Dialog", "Upload"))
        self.quit_btn.setText(_translate("Dialog", "Quit"))
        self.total_objects_label.setText(_translate("Dialog", "Total Objects: 0"))
        self.send_btn.setText(_translate("Dialog", "Send"))
