
    
    
    
    # -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 22:37:46 2016

@author: pfduc
"""
from hsk_flashcard import FlashCardBrowser
    
from PyQt4.QtGui import QFileDialog,QFont,QWidget, QVBoxLayout, QLabel,QApplication,QPushButton, QMessageBox
from PyQt4.QtCore import SIGNAL
import sys

app = QApplication(sys.argv)
QFileDialog.getSaveFileName(None,'Save as', './',"HSK_Level_5.csv")
#ex.show()
sys.exit(app.exec_())