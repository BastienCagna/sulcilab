import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QDialog, QLineEdit, QPushButton
import PyQt5.QtWidgets as qtw

from sulcilab.database import SessionLocal
from sulcilab.core.user import login, PUserSignIn

class SignInDialog(QDialog):
    user_signed_in = pyqtSignal(str, name="UserSignedIn")

    def __init__(self, parent=None):
        super(SignInDialog, self).__init__(parent)
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

        self.buttonLogin.clicked.connect(self.handleLogin)

    def handleLogin(self):
        ulogin = PUserSignIn(email="admin", password="admin")
        token = login(ulogin, SessionLocal())
        # if (self.textName.text() == 'foo' and
        #     self.textPass.text() == 'bar'):
        #     self.accept()
        # else:
        #     qtw.QMessageBox.warning(
        #         self, 'Error', 'Bad user or password')
        token = "1DKENEZdcmkjbzeîuzedmjzkczmiecjbeimub"
        self.user_signed_in.emit(token)
        self.hide()