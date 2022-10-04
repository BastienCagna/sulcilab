import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
import PyQt5.QtWidgets as qtw

from sulcilab_gui.windows import MainWindow

APP_NAME = "SulciLab GUI"

class SulciLabGUIApp (qtw.QApplication):
    def __init__(self, argv: typing.List[str]) -> None:
        super().__init__(argv)
        self.main_window = MainWindow(APP_NAME)
            
def window():
   app = SulciLabGUIApp(sys.argv)
   sys.exit(app.exec_())

if __name__ == '__main__':
   window()
