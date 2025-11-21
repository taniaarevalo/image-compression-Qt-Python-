from PySide6.QtWidgets import QMainWindow, QErrorMessage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def display_error_message(self, error_message):
        error_dialog = QErrorMessage()
        error_dialog.showMessage(error_message)
        error_dialog.exec()
