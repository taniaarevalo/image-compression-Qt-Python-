"""
NOM: Arévalo
PRÉNOM: Tania
SECTION: B1-INFO
MATRICULE: 000570504
"""

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QTextEdit, QMessageBox, QErrorMessage, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QDialog
from PySide6.QtGui import QPixmap, QColor, QPainter, QImage
from PySide6.QtCore import *
from encoding import Encoder, Decoder
from pixel import Pixel
import sys

# Première chose à faire, c'est Import les fichiers et modules importants. 
# Aide apportée par la documentation et vidéos youtube expliquant les méthodes, imports, etc.

class ImageCreation(QWidget):  # Classe crée l'image de l'interface graphique.
    def __init__(self, file):  # Dans son constructeur il faut placer le fichier dans lequel se trouve l'image.
        super().__init__()  
        self.image_class = Decoder.load_from(file)  # L'image est envoyée à la fonction statique du fichier Decoder, pour la transformer en classe Image contenant la width/height/liste de pixels.
        
        self.setMinimumSize(self.image_class.width, self.image_class.height)  

    def paintEvent(self, event):  # Fonction s'occupant de peindre l'image. (Utiliser event pour faire les scales correctement?)
        self.paint_image = QPainter(self)  # Pour peindre.
        if self.image_class is not None:  
            painter = QPainter(self)  # Pour peindre.
            image = QImage(self.image_class.width, self.image_class.height, QImage.Format_RGB888)  # image dans laquelle on peint.
            for y in range(self.image_class.height):  # coordonnées pour indiquer où peindre
                for x in range(self.image_class.width):
                    index = y * self.image_class.width + x
                    if index < len(self.image_class.pixels):
                        r = self.image_class.pixels[index].rouge  # enregistrement de chaque couleur du pixel
                        g = self.image_class.pixels[index].vert
                        b = self.image_class.pixels[index].bleu
                        color = QColor(r, g, b)
                        image.setPixelColor(x, y, color) 
            painter.drawImage(0, 0, image)
        self.paint_image.end()

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compression d'une image")  # titre de la fenêtre

        self.load_button = QPushButton("Load Image")  # premier bouton pour charger l'image
        self.load_button.clicked.connect(self.load_image)  # est sensé ouvrir les fichiers de l'ordinateur de l'utilisateur pour qu'il choisisse.
        self.load_button.setFont("Georgia")
        self.load_button.setStyleSheet('color:pink')
        self.load_button.setAutoRepeat(False)

        self.save_button = QPushButton("Save Image") # deuxième bouton pour sauvegarder l'image. Dans la version demandée ?
        self.save_button.clicked.connect(self.save_image) 
        self.save_button.setFont("Georgia")
        self.save_button.setStyleSheet('color:pink')
        self.save_button.setEnabled(False)

        layout = QVBoxLayout()  # Layout fait à l'horizental.
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # self.setLayout(layout)
        self.image_file = None

        self.messages_erreurs = None

        self.file_name = None

    
    def load_image(self):  # mettre cette image avec les boutons (refaire boutons? les mettre dans une classe à part? et les appeller deux fois, une fois avec écran une fois sans )

        self.file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File.")  # Chercher images désirée.  # QFileDialog ouvre les fichiers pour pouvoir en choisir un.

        # Il faut d'abord regarder s'il y a des erreurs. 
        with open(self.file_name, 'rb') as f: 
            image_bytes = f.read() 

        if image_bytes[:5] != b'ULBMP':  # Vérifier si l'extension est la bonne.
            self.error_message("Le header 'ULBMP' n'est pas correctement écrit.")

        header = int.from_bytes(image_bytes[6:8], byteorder = 'little')

        palette = int.from_bytes(image_bytes[12:13], byteorder = 'little')

        version = int.from_bytes(image_bytes[5:6], byteorder = 'little')  # tester la version
        versions_possibles = [1, 2, 3, 4]
        if version not in versions_possibles:
            self.error_message("Cette version n'existe pas.")

        width = int.from_bytes(image_bytes[8:10], byteorder = 'little')
        height = int.from_bytes(image_bytes[10:12], byteorder = 'little')
        if version == 3:
                profondeur = int.from_bytes(image_bytes[12:13], byteorder = 'little')
                rle = int.from_bytes(image_bytes[13:14], byteorder = 'little')
                profondeurs_possibles = [1, 2, 4, 8, 24]
                rle_possibles =  [0, 1]
                if profondeur not in profondeurs_possibles: 
                    self.error_message("La profondeur n'est pas correcte.")
                if rle not in rle_possibles:
                    self.error_message("La rle n'est pas correcte.")
                if (rle == 0 and profondeur > 4) or (rle == 1 and profondeur < 8):
                    self.error_message("La rle et la profondeur ne vont pas ensemble.")  

        if self.file_name:
            self.image_file = ImageCreation(self.file_name)  # On l'envoie dans une classe qui s'occupera de son initialisation sur l'écran.
            layout = QVBoxLayout()  # choix du layout pour l'image
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.load_button)
            button_layout.addWidget(self.save_button)
            self.save_button.setEnabled(True)
            layout.addLayout(button_layout)
            layout.addWidget(self.image_file)  # on rajoute

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

    def save_image(self):
        version = int(input("En quelle version désirez-vous compresser l'image? Vous avez quatre choix: 1, 2, 3 ou 4! "))  # demander version 
        if version > 4 or version < 1:
            self.error_message("Mauvaise version écrite.")

        if version == 3:
            profondeurs_possibles = [1, 2, 4, 8, 24]
            profondeur = int(input("En quelle profondeur? Vous avez cinq choix: 1, 2, 4, 8 ou 24! "))
            if profondeur not in profondeurs_possibles:
                self.error_message("Profondeur n'est pas compatible avec le code!")
                
            rle = str(input("En quelle rle? Vous avez deux choix: True ou False! "))
            if rle == 'True':
                rle = True
            elif rle == 'False':
                rle = False
            if (rle is False and profondeur > 4) or (rle is True and profondeur < 8):
                self.error_message("Rle non compatible avec la profondeur!")
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Compressed Image", "", "Compressed Image Files (*.ulbmp)")
        """if file_name:
            compressed_image.save(file_name, 'ULBMP')"""

        if version == 1 or version == 2:
            image_class = Decoder.load_from(self.file_name)
            encoder = Encoder(image_class, version)
            encoder.save_to(file_name)
        
        elif version == 3:
            valeurs_sup = {"depth": profondeur, "rle": rle}
            image_class = Decoder.load_from(self.file_name)
            encoder = Encoder(image_class, version, **valeurs_sup)
            encoder.save_to(file_name)
    
    def error_message(self, message):
        error = QErrorMessage()
        error.showMessage(message)
        error.exec()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyWindow()
    window.show()
    app.exec()