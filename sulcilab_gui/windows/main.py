import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
import PyQt5.QtWidgets as qtw

# import anatomist.api as anatomist

from sulcilab_gui.dialogs import SignInDialog


class MainWindow (qtw.QMainWindow):
    _anatomist_instance = None

    def __init__(self, app_name:str, token=None) -> None:
        super().__init__()
        self.user_token = token
        self.setGeometry(200,200,400,200)
        self.setWindowTitle(app_name)

        self.sigin_dialog = SignInDialog(self)
        self.sigin_dialog.user_signed_in.connect(self.set_user_token)
        
        self.sigin_dialog.show()

    def set_user_token(self, token:str):
        self.user_token = token

        b = qtw.QLabel(self)
        b.setText("User token: " + self.user_token)
        b.move(50,20)
        self.show()

    def show(self):
        if not self.user_token:
            return
        super().show()

        # # lazy creation of an anatomist instance
        # if MainWindow._anatomist_instance is None:
        #     MainWindow._anatomist_instance = anatomist.Anatomist()
        # self._instance = MainWindow._anatomist_instance
