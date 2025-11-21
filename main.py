"""
NOM: Arévalo
PRÉNOM: Tania
SECTION: B1-INFO
MATRICULE: 00570504
"""
from PySide6.QtWidgets import QApplication, QMainWindow
from window import *
import sys
# Code s'occupant de l'organisation de tout le projet 2 et de l'utilisation de l'interface.

def main():
    MyWindow()  # Classe MyWindow, dans window.py.

if __name__ == "__main__":  
    app = QApplication(sys.argv)

    window = MyWindow()
    window.show()
    app.exec()
