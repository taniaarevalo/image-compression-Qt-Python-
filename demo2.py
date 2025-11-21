from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtGui import QPainter, QColor, QImage, QPixmap
import sys

class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Sample image data for testing
        image_data = b'\x55\x4c\x42\x4d\x50\x01\x0c\x00\x00\x02\x00\x01\x00\x00\x00\x00\x00\x00'
        header = image_data[:12]
        version = header[5]
        header_size = int.from_bytes(header[6:8], byteorder='little')
        width = int.from_bytes(header[8:10], byteorder='little')
        height = int.from_bytes(header[10:12], byteorder='little')

        # Create QImage
        image = QImage(width, height, QImage.Format_RGB888)
        image.fill(Qt.white)  # Fill with white background

        # Draw the QImage onto the widget
        painter.drawImage(0, 0, image)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 400, 400)

        # Create Load Image button
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)

        # Create ImageWidget
        self.image_widget = ImageWidget()

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.load_image_button)
        layout.addWidget(self.image_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File.")
        if file_name:
            pixmap = QPixmap(file_name)
            self.image_widget.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
