import typing
# from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
import PyQt5.QtWidgets as qtw
from pytest import Session

import jwt
# import anatomist.api as anatomist

from sulcilab_gui.dialogs import SignInDialog
from sulcilab_gui.widgets import CollapsibleBox
from sulcilab.database import SessionLocal
from sulcilab.brainvisa.database import read, PDatabase
from sulcilab.brainvisa.subject import PSubject


class SubjectWidget(CollapsibleBox):
    def __init__(self, parent, subject:PSubject):
        # super(CollapsibleBox, self).__init__(subject.name, parent)
        super().__init__(subject.name, parent)
        self.subject = subject

        layout = qtw.QVBoxLayout(self)
        layout.addWidget(qtw.QLabel("Espèce: " + (subject.species.fr_name if subject.species else "N.C"), self))
        layout.addWidget(qtw.QLabel("Centre: " + (subject.center if subject.center else "N.C"), self))
        for graph in subject.graphs:
            layout.addWidget(qtw.QLabel(str(graph.version) + " | " +str(graph.hemisphere)))
        self.setContentLayout(layout)
        # for lset in subject.l
        # self.subject_name = qtw.QLabel(subject.name, self)        

        # self.layout.addWidget(self.subject_name)
        # self.setLayout(self.layout)


class DatabaseExplorerWidget(QWidget):
    def __init__(self, parent, database:PDatabase):
        super(QWidget, self).__init__(parent)
        self.layout = qtw.QVBoxLayout(self)
        self.database = database

        for subject in self.database.subjects:
            self.layout.addWidget(SubjectWidget(self, subject))
        self.setLayout(self.layout)
    
class DatabasesExplorerTabsWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = qtw.QVBoxLayout(self)
        
        self.tabs = qtw.QTabWidget()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.load()
    
    def load(self):
        self.databases = read(db=SessionLocal())
        for i in range(self.tabs.count()):
            self.tabs.removeTab(i)
        for db in self.databases:
            tab = DatabaseExplorerWidget(self, db)
            self.tabs.addTab(tab, db.name)


class MainWindow (qtw.QMainWindow):
    _anatomist_instance = None

    def __init__(self, app_name:str, token=None) -> None:
        super().__init__()
        self.user_token = token
        self.resize(600, 800)
        self.setWindowTitle(app_name)
        self._create_actions()
        # self._create_menu_bar()
        self._create_toolbar()

        self.tabs = DatabasesExplorerTabsWidget(self)
        self.setCentralWidget(self.tabs)

        # First, ask to connect
        self.sigin_dialog = SignInDialog(self)
        self.sigin_dialog.user_signed_in.connect(self.set_user_token)

        self._reset()

    def _create_actions(self):
        # self.open_action = qtw.QAction("&Open...", self)
        # list of built in icons: https://www.pythonguis.com/faq/built-in-qicons-pyqt/
        # how to add custom icons: https://realpython.com/python-menus-toolbars/#:~:text=in%20this%20tutorial.-,Creating%20Menu%20Bars,()%20on%20your%20QMainWindow%20object.
        # self.logout_action = qtw.QAction(self.style().standardIcon(qtw.QStyle.SP_ArrowBack), "&Logout", self)
        self.reload_action = qtw.QAction(self.style().standardIcon(qtw.QStyle.SP_BrowserReload), "&Reload", self)
        self.reload_action.triggered.connect(self.reload)
        self.logout_action = qtw.QAction("&Logout", self)
        self.logout_action.triggered.connect(self.logout)
        # self.exit_action = qtw.QAction("&Exit", self)

    def _create_toolbar(self):
        tb = self.addToolBar("Menu")
        tb.setMovable(False)

        self.username_label = qtw.QLabel(self)
        tb.addWidget(self.username_label)

        tb.addAction(self.logout_action)
        tb.addAction(self.reload_action)
        # tb.addAction(self.exit_action)

        # tb.setToolButtonStyle(Qt.ToolButtonIconOnly)

    # def __init__(self, parent=None):
    #     # Snip...
    #     self._createContextMenu()
    # def _createContextMenu(self):
    #     # Setting contextMenuPolicy
    #     self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
    #     # Populating the widget with actions
    #     self.centralWidget.addAction(self.newAction)
    #     self.centralWidget.addAction(self.openAction)
    #     self.centralWidget.addAction(self.saveAction)
    #     self.centralWidget.addAction(self.copyAction)
    #     self.centralWidget.addAction(self.pasteAction)
    #     self.centralWidget.addAction(self.cutAction)

    def _reset(self):
        self.hide()
        # self.sigin_dialog.show()
        self.set_user_token("fake_token")

    def set_user_token(self, token:str):
        self.user_token = token
        username = "Bastien" #jwt.decode(token, algorithms="HS256", options={"verify_signature": False})['username']
        self.username_label.setText("User: " + username)
        self.show()

    def logout(self):
        self.user_token = None
        self._reset()

    def reload(self):
        self.tabs.load()

    def show(self):
        if not self.user_token:
            return
        super().show()

        # # lazy creation of an anatomist instance
        # if MainWindow._anatomist_instance is None:
        #     MainWindow._anatomist_instance = anatomist.Anatomist()
        # self._instance = MainWindow._anatomist_instance
