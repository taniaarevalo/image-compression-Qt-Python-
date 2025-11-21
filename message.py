from PySide6.QtWidgets import QWidget, QMessageBox, QPushButton


class Message(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMessage Box")

        button = QPushButton('Hard')
        button.clicked.connect(self.button_clicked)

        button_critical = QPushButton("Critical")
        button_critical.clicked.connect(self.button_clicked_critical)

        button_question = QPushButton("Question")
        button_question.clicked.connect(self.button_clicked_question)

        button_information = QPushButton("Information")
        button_information.clicked.connect(self.button_clicked_information)

        button_warning = QPushButton("Warning")
        button_warning.clicked.connect(self.button_clicked_warning)
        
        boite = QMessageBox()
        boite.setMinimumSize(700, 200)