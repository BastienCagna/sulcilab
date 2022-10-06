import typing
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QDialog, QLineEdit, QPushButton, QLabel
import PyQt5.QtWidgets as qtw
import fastapi
import sys
from sulcilab.database import SessionLocal
from sulcilab.core.user import login, PUserSignIn


class SignInDialog(QDialog):
    user_signed_in = pyqtSignal(str, name="UserSignedIn")

    def __init__(self, parent=None):
        super(SignInDialog, self).__init__(parent)
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.textPass.setEchoMode(QLineEdit.Password)
        self.message = QLabel(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.buttonExit = QPushButton('Quit', self)
        self.buttonExit.clicked.connect(self.handleExit)
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)
        layout.addWidget(self.buttonExit)
        layout.addWidget(self.message)

        self.buttonLogin.clicked.connect(self.handleLogin)

    def handleLogin(self):
        ulogin = PUserSignIn(
            email=self.textName.text(), 
            password=self.textPass.text()
        )
        try:
            response = login(ulogin, SessionLocal())
        except fastapi.exceptions.HTTPException:
            self.message.setText("Wrong credentials")
        else:
            self.user_signed_in.emit(response['token'])
            self.hide()

    def handleExit(self):
        sys.exit()