import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
import paramiko
import os

class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Client')
        
        layout = QVBoxLayout()
        
        self.label = QLabel("No image selected", self)
        layout.addWidget(self.label)
        
        self.chooseBtn = QPushButton('Choose Image', self)
        self.chooseBtn.clicked.connect(self.choose_image)
        layout.addWidget(self.chooseBtn)
        
        self.sendBtn = QPushButton('Send Image', self)
        self.sendBtn.clicked.connect(self.send_image)
        layout.addWidget(self.sendBtn)
        
        self.setLayout(layout)
        self.image_path = None
    
    def choose_image(self):
        options = QFileDialog.Options()
        self.image_path, _ = QFileDialog.getOpenFileName(self, "Choose Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if self.image_path:
            self.label.setText(os.path.basename(self.image_path))
    
    def send_image(self):
        if self.image_path:
            host = "127.0.0.1"  # Replace with actual server IP
            port = 22
            username = "MSI"
            key_file = os.path.expanduser('~/.ssh/id_rsa')  # Path to your private key file
            remote_path = "/home/MSI/images"  # Default remote path
            
            try:
                key = paramiko.RSAKey.from_private_key_file(key_file)
                transport = paramiko.Transport((host, port))
                transport.connect(username=username, pkey=key)
                
                sftp = paramiko.SFTPClient.from_transport(transport)
                sftp.put(self.image_path, os.path.join(remote_path, os.path.basename(self.image_path)))
                sftp.close()
                transport.close()
                
                self.label.setText("Image sent successfully!")
            except Exception as e:
                self.label.setText(f"Error: {str(e)}")
        else:
            self.label.setText("No image selected")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ClientApp()
    client.show()
    sys.exit(app.exec_())
