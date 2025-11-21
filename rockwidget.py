"""
NOM: Arévalo
PRÉNOM: Tania
SECTION: B1-INFO
MATRICULE: 00570504
"""

from PySide6.QtWidgets import QFileDialog, QWidget
from PySide6.QtCore import QDir
from PySide6.QtGui import *
import os, sys

class imageManip(QWidget):
    def __init__(self):
        img = QImage(1000, 1000, QImage.Format('ulbmp'))
        img.load(self.file_load())

    def file_load(self):
        dialog = QFileDialog()
        dialog.getOpenFileNames(QFileDialog.AnyFile)
        file = dialog.setFilter(QDir.Files)
        return file
    
app = QGuiApplication(sys.argv)

window = imageManip()
window.show()
sys.exit(app.exec())
