from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog
from PySide6.QtGui import QPainter, QColor, QImage
import sys

class ImageWidget(QWidget):  # custom widget displays image.
    def __init__(self, image_data):  # input data
        super().__init__()
        self.image_data = image_data  # mettre au début? ou laisser a être initialise après

    def paintEvent(self, event):  # when a widget needs to be repainted
        painter = QPainter(self)  # Qpainter created paints in widget
        painter.setRenderHint(QPainter.Antialiasing)  # for smoother rendering

        # Parse the header
        header = self.image_data[:12]  # header.
        version = header[5]  # version importante pr après
        header_size = int.from_bytes(header[6:8], byteorder='little')  # taille header
        width = int.from_bytes(header[8:10], byteorder='little')  # width
        height = int.from_bytes(header[10:12], byteorder='little')  # height

        # Parse pixel data
        pixel_data = self.image_data[12:]
        pixels = [pixel_data[i:i+3] for i in range(0, len(pixel_data), 3)]

        # Create QImage
        image = QImage(width, height, QImage.Format_RGB888)

        # Paint pixels onto QImage
        for y in range(height):
            for x in range(width):
                index = y * width + x
                if index < len(pixels):
                    r, g, b = pixels[index]
                    color = QColor(r, g, b)
                    image.setPixelColor(x, y, color)

        # Draw the QImage onto the widget
        painter.drawImage(0, 0, image)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File.")
        
        # Sample image data
        file = open(file_name, 'rb') #le mettre quelque part pour le manipuler
        image_data = file.read()
        
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 400, 400)

        # Create ImageWidget
        self.image_widget = ImageWidget(image_data)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
