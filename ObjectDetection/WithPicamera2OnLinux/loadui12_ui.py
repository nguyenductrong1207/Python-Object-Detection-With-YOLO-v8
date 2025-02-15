# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Github\Object-Detection-With-Python\ObjectDetection\Picamera\download\loadui12.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1500, 800)
        Dialog.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.TEXT = QtWidgets.QTextBrowser(Dialog)
        self.TEXT.setGeometry(QtCore.QRect(410, 30, 671, 41))
        self.TEXT.setObjectName("TEXT")
        self.imgLabel = QtWidgets.QLabel(Dialog)
        self.imgLabel.setGeometry(QtCore.QRect(49, 0, 800, 700))
        self.imgLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imgLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imgLabel.setLineWidth(6)
        self.imgLabel.setText("")
        self.imgLabel.setObjectName("imgLabel")
        self.processedImgLabel = QtWidgets.QLabel(Dialog)
        self.processedImgLabel.setGeometry(QtCore.QRect(49, 0, 1000, 1000))
        self.processedImgLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.processedImgLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.processedImgLabel.setLineWidth(6)
        self.processedImgLabel.setText("")
        self.processedImgLabel.setObjectName("processedImgLabel")
        self.frameRight = QtWidgets.QFrame(Dialog)
        self.frameRight.setGeometry(QtCore.QRect(37, 77, 1400, 550))
        self.frameRight.setFrameShape(QtWidgets.QFrame.Box)
        self.frameRight.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameRight.setObjectName("frameRight")
        self.CAMERA = QtWidgets.QPushButton(Dialog)
        self.CAMERA.setGeometry(QtCore.QRect(30, 670, 111, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.CAMERA.setFont(font)
        self.CAMERA.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.CAMERA.setObjectName("CAMERA")
        self.CAPTURE = QtWidgets.QPushButton(Dialog)
        self.CAPTURE.setGeometry(QtCore.QRect(680, 710, 120, 55))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.CAPTURE.setFont(font)
        self.CAPTURE.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.CAPTURE.setObjectName("CAPTURE")
        self.UNDO = QtWidgets.QPushButton(Dialog)
        self.UNDO.setGeometry(QtCore.QRect(320, 670, 111, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.UNDO.setFont(font)
        self.UNDO.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.UNDO.setObjectName("UNDO")
        self.QUIT = QtWidgets.QPushButton(Dialog)
        self.QUIT.setGeometry(QtCore.QRect(1330, 660, 93, 28))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(240, 2, 2))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 248, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 2, 2))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 248, 44))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 2, 2))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.QUIT.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setBold(True)
        font.setWeight(75)
        self.QUIT.setFont(font)
        self.QUIT.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.QUIT.setObjectName("QUIT")
        self.UPLOAD = QtWidgets.QPushButton(Dialog)
        self.UPLOAD.setGeometry(QtCore.QRect(170, 670, 111, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.UPLOAD.setFont(font)
        self.UPLOAD.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.UPLOAD.setObjectName("UPLOAD")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.CAMERA.setText(_translate("Dialog", "Camera"))
        self.CAPTURE.setText(_translate("Dialog", "Capture"))
        self.UNDO.setText(_translate("Dialog", "Undo"))
        self.QUIT.setText(_translate("Dialog", "Quit"))
        self.UPLOAD.setText(_translate("Dialog", "Upload"))
