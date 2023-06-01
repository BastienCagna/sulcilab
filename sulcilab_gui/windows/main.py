import typing
from uuid import uuid4
# from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import QtGui
import PyQt5.QtWidgets as qtw
from warnings import warn
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from sulcilab.brainvisa import labelingset
from sulcilab_gui.dialogs import SignInDialog
from sulcilab_gui.dialogs.new_labelingset import NewLabelingSetDialog
from sulcilab.database import SessionLocal
from sulcilab.brainvisa.database import read
from sulcilab.brainvisa.subject import Subject
from sulcilab.brainvisa.graph import Graph, Hemisphere
from sulcilab.core.user import get_current_user, User
from sulcilab.database import SQLALCHEMY_DATABASE_URL
import anatomist.api as ana
from enum import Enum
import os.path as op


DEFAULT_SULCAL_NOMENCLATURE = "default"
DEFAULT_GEOMETRY = [133, 93, 747, 516]
class PointOfView(Enum):
    Left_to_Right = [0.5, 0.5, 0.5, 0.5]
    Right_to_Left = [0.5, -0.5, -0.5, 0.5]

DEFAULT_HIE_FILE = op.join(op.split(__file__)[0], '..', '..', 'data', 'sulcal_root_colors.hie')


class Anatomist:
    def __init__(self):
        self.message_callback = None
        self._reset()

    def _check_instance(self):
         if self._instance is None:
            self._send_message("Starting Anatomist...")
            self._instance = ana.Anatomist()
            self._send_message("Done", 2000)

    def _reset(self):
        self._instance = None
        self._objects = {}
        self._windows = {}
        self.hie = None

    def _send_message(self, message, msecs=0):
        if self.message_callback:
            self.message_callback(message, msecs)

    def register_message_callback(self, callback):
        if self.message_callback:
            self._send_message("Last message. An other callback isbeing set.")
        self.message_callback = callback

    def close(self):
        if self._instance:
            # FIXME: it close the main window and not anatomist...
            self._instance.execute('exit')
        self._reset()

    def load(self, fname, register=True):
        self._check_instance()
        if fname in self._objects.keys():
            raise NotImplementedError("Reload of object is not implemented")
        o = self._instance.loadObject(fname)
        if register:
            self._objects[fname] = o
        return o

    def new_window(self, wname=None, type="3D", geometry=None, options=None):
        self._check_instance()        
        if wname is None:
            wname = uuid4()
        if wname in self._windows.keys():
            raise NotImplementedError("Reuse of window is not implemented")
        self._windows[wname] = self._instance.createWindow(type, geometry=geometry, options=options)
        return self._windows[wname]

    def show_labeled_graph(self, mesh_f, graph_f, point_of_view, hie_f=DEFAULT_HIE_FILE, save_as=None, geometry=DEFAULT_GEOMETRY):
        if not self.hie:
            self.hie = self.load(hie_f, register=False)
        mesh = self.load(mesh_f)
        graph = self.load(graph_f)
        graph.setLabelProperty('name')

        # view an object
        win = self.new_window(type="3D", geometry=geometry, options={"no_decoration": True})
        # win.addObjects([mesh])
        win.addObjects([mesh, graph], add_graph_nodes=True)
        win.camera(view_quaternion=point_of_view.value)
        win.windowConfig(cursor_visibility=0)
        if save_as:
            win.snapshot(save_as)
            # del win, mesh, graph

    def close(self):
        if self._instance:
            self._instance.close()


class BrowserWidget(qtw.QWidget):
    subject_selected = pyqtSignal(Subject, name="SubjectSelected")

    def __init__(self, parent, session):
        super(qtw.QWidget, self).__init__(parent)
        self.session = session

        layout = qtw.QVBoxLayout(self) 
        
        self.db_listitems = qtw.QListWidget()
        self.db_listitems.itemClicked.connect(self.select_database)
        self.sub_listitems = qtw.QListWidget()
        self.sub_listitems.itemClicked.connect(self.select_subject)
        # self.dock.setWidget(self.tabs)

        self.current_database = None
        
        layout.addWidget(qtw.QLabel("Databases", self))
        layout.addWidget(self.db_listitems)
        layout.addWidget(qtw.QLabel("Subjects", self))
        layout.addWidget(self.sub_listitems)
        self.setLayout(layout)
        self.load()
    
    def load(self):
        databases = read(db=self.session)
        self.db_listitems.clear()
        self.sub_listitems.clear()
        self.databases = []
        for db in databases:
            self.db_listitems.addItem(db.name)
            self.databases.append(db)

    def select_database(self, item: qtw.QListWidgetItem):
        self.sub_listitems.clear()
        self.current_database = None
        qname = item.text()
        for db in self.databases:
            if db.name == qname:
                self.current_database = db
                break
        if not self.current_database :
            warn(f"Database {qname} not found in the list.")
        else:
            self.sub_listitems.addItems(sorted(s.name for s in self.current_database.subjects))

    def select_subject(self, item:qtw.QListWidgetItem):
        qname = item.text()
        subject = None
        for sub in self.current_database.subjects:
            if sub.name == qname:
                subject = sub
                break
        if not subject:
            warn(f'Subject {qname} not found in database {self.current_database.name}.')
        else:
            self.subject_selected.emit(subject)


class LabelingSetControlsWidget(qtw.QWidget):
    def __init__(self, labelingset: labelingset.LabelingSet, anatomist:Anatomist, token:str, session:Session, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.lset = labelingset
        self.anatomist = anatomist
        self.token = token
        self.session = session

        layout = qtw.QVBoxLayout(self)
        self.nom_label = qtw.QLabel("Nomenclature: " + self.lset.nomenclature.name)
        layout.addWidget(self.nom_label)

        sub_layout = qtw.QHBoxLayout(self)
        self.open_graph_btn = qtw.QPushButton("View", self)
        self.open_graph_btn.clicked.connect(self.open_graph)
        sub_layout.addWidget(self.open_graph_btn)
        self.edit_btn = qtw.QPushButton("Edit", self)
        self.edit_btn.clicked.connect(self.edit)
        sub_layout.addWidget(self.edit_btn)
        self.export_btn = qtw.QPushButton("Export...", self)
        # self.export_btn.clicked.connect(self.open_graph)
        sub_layout.addWidget(self.export_btn)
        self.delete_btn = qtw.QPushButton("Delete", self)
        self.delete_btn.clicked.connect(self.delete)
        sub_layout.addWidget(self.delete_btn)
        layout.addLayout(sub_layout)

        layout.addWidget(qtw.QLabel("Comments:", self))
        self.comment_input = qtw.QPlainTextEdit(self.lset.comment, self)
        self.comment_input.setMinimumHeight(3 * qtw.QSizePolicy.Preferred)
        self.comment_input.setEnabled(False)
        layout.addWidget(self.comment_input)

        self.save_btn = qtw.QPushButton("Save changes")
        self.save_btn.clicked.connect(self.save)
        # self.setStyleSheet("background-color: green")
        self.save_btn.hide()
        layout.addWidget(self.save_btn)

        layout.addWidget(self.comment_input)
        self.setLayout(layout)

    def open_graph(self):
        graph:Graph = self.lset.graph
        self.anatomist.show_labeled_graph(
            graph.get_mesh_path(),
            graph.get_path(),
            PointOfView.Left_to_Right if graph.hemisphere.value == "L" else PointOfView.Right_to_Left
        )

    def edit(self):
        self.comment_input.setEnabled(True)
        self.save_btn.show()
        self.open_graph()

    def save(self):
        # Get the text comment
        self.lset.comment = self.comment_input.toPlainText()

        # Get the graph from anatomist
        # self.anatomist

        # Get the nomenclature

        # Modify each labelings to match th graph

        # Save labelings

        # Save labelingset
        
        lset = labelingset.save_labelingset(
            self.lset, self.token, self.session
        )
        print("saved =D")
        pass

    def delete(self):
        msg = qtw.QMessageBox()
        msg.setIcon(qtw.QMessageBox.Warning)
        msg.setText("Are you sure to delete the labeling set?")
        msg.setWindowTitle("Confirm deletion")
        msg.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)
        r = msg.exec_()
        if r == qtw.QMessageBox.Yes :
            labelingset.delete_labelingset(self.lset, self.token, self.session)
            # TODO: really remove the widget?
            self.hide()


class SubjectHemisphereControlsWidget(qtw.QWidget):
    def __init__(self, h:str, anatomist: Anatomist, db: Session, parent = None):
        super(qtw.QWidget, self).__init__(parent)
        self.anatomist = anatomist
        self.subject = None
        self.user = None
        self.token = None
        self.session = db
        if h not in ['L', 'R']:
            raise ValueError(f'Hemisphere is expected to be "L" or "R" not "{str(h)}".')
        self.hemi = h
        self.hemisphere = "Left" if h == "L" else "Right"
        self._create_ui()
        self.reset()

    def _create_ui(self):
        if self.layout():
            qtw.QWidget().setLayout(self.layout())
        layout = qtw.QVBoxLayout(self)

        self.title_label = qtw.QLabel(self.hemisphere + " hemisphere", self)
        self.title_label.setFont(QtGui.QFont('Arial', 10, weight=QtGui.QFont.Bold))
        layout.addWidget(self.title_label)

        self.new_btn = qtw.QPushButton("New", self)
        self.new_btn.clicked.connect(self.new_labelingset)
        self.new_btn.setEnabled(self.user is not None and self.subject is not None)
        layout.addWidget(self.new_btn)
            
        if self.subject and self.user:
            subject_graph_ids = list(g.id for g in self.subject.graphs)
            labelinsets = []
            for lset in self.user.labelingsets:
                if lset.graph.id in subject_graph_ids:
                    labelinsets.append(lset)

            self.lsets_widgets = []
            for lset in labelinsets:
                w = LabelingSetControlsWidget(lset, self.anatomist, self.token, self.session, self)
                self.lsets_widgets.append(w)
                layout.addWidget(w)
        self.setLayout(layout)

    def reset(self):
        self.user = None
        self.subject = None
        self.graph = None

    def set_user(self, token: str, user:str):
        """ Set the JWT token and associated user to allow the widget to query the database """
        self.user = user
        self.token = token

    def set_subject(self, subject: Subject):
        self.subject = subject

        if not self.user:
            raise RuntimeError("User isn't set. Cannot access to the database.")
        self._create_ui()

    def new_labelingset(self):
        graph = self.subject.get_one_graph(hemisphere=self.hemi)
        if graph is None:
            # src: https://www.tutorialspoint.com/pyqt/pyqt_qmessagebox.htm
            msg = qtw.QMessageBox()
            msg.setIcon(qtw.QMessageBox.Warning)
            msg.setText(f"{self.subject.name} has no graph for the {self.hemisphere} hemisphere. No new labeling set can be added.")
            msg.setWindowTitle("No graph found")
            msg.setStandardButtons(qtw.QMessageBox.Close)
            msg.exec_()
            return
        
        dialog = NewLabelingSetDialog(self.user, graph, self.token, self.session, self)
        dialog.exec_()
        if dialog.labeling_set:
            self.user.labelingsets.append(dialog.labeling_set)
            self._create_ui()


class SubjectWidget(qtw.QWidget):
    def __init__(self, anatomist: Anatomist, database: Session, parent = None):
        super(qtw.QWidget, self).__init__(parent)
        self.anatomist = anatomist
        self.database = database
        self._create_ui()
        self.reset()

    def _create_ui(self):
        layout = qtw.QVBoxLayout(self)

        self.name_label = qtw.QLabel(self)
        self.name_label.setFont(QtGui.QFont('Arial', 14, weight=QtGui.QFont.Bold))
        self.species_label = qtw.QLabel(self)
        self.center_label = qtw.QLabel(self)

        verticalSpacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        self.left_controls = SubjectHemisphereControlsWidget("L", self.anatomist, self.database, self)
        self.right_controls = SubjectHemisphereControlsWidget("R", self.anatomist, self.database, self)

        layout.addWidget(self.name_label)
        layout.addWidget(self.species_label)
        layout.addWidget(self.center_label)
        layout.addWidget(self.left_controls)
        layout.addWidget(self.right_controls)
        layout.addItem(verticalSpacer)
        self.setLayout(layout)

    def reset(self):
        self.user = None
        self.current_subject = None
        self.name_label.setText('')
        self.species_label.setText("Select a subject")
        self.center_label.setText('')

    def set_user(self, token:str, user:User):
        self.user = user
        self.left_controls.set_user(token, user)
        self.right_controls.set_user(token, user)

    def set_subject(self, subject:Subject):
        self.current_subject = subject
        self.left_controls.set_subject(subject)
        self.right_controls.set_subject(subject)

        self.name_label.setText(subject.database.name + "/ " + subject.name)
        self.species_label.setText("Species: " + (subject.species.fr_name if subject.species else 'N.C'))
        self.center_label.setText(f"Center: {subject.center}")
# TODO: setup a better conversion of loaded objects (refactor)

class SlLogger:
    def __init__(self):
        self.history = []
        self.callbacks = []

    def register(self, callback):
        self.callbacks.append(callback)

    def log(self, message: str, msecs=0):
        fmt_date = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(fmt_date + ": " + message)
        for callback in self.callbacks:
            try:
                callback(message, msecs)
            except TypeError:
                callback(message)

class MainWindow (qtw.QMainWindow):
    def __init__(self, app_name:str, token=None) -> None:
        super().__init__()
        self.resize(600, 800)
        self.setWindowTitle(app_name)
        self._create_actions()
        # self._create_menu_bar()
        self._create_toolbar()

        self.status_bar = qtw.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.username_label = qtw.QLabel(self)
        self.status_bar.addPermanentWidget(self.username_label)

        self.logger = SlLogger()
        self.logger.register(self.set_status_message)
        self.anatomist = Anatomist()
        self.anatomist.register_message_callback(self.logger.log)
        self.session = SessionLocal()

        self.browser = BrowserWidget(self, self.session)
        self.dock = qtw.QDockWidget("Browser")
        self.dock.setWidget(self.browser)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.viewer = SubjectWidget(self.anatomist, self.session, self)
        self.browser.subject_selected.connect(self.viewer.set_subject)
        # self.viewer.left_controls.open_graph.connect(self.open_graph)
        # self.viewer.right_controls.open_graph.connect(self.open_graph)
        self.setCentralWidget(self.viewer)
        # layout = qtw.QHBoxLayout(self)
        # layout.addWidget(self.browser)
        # self.setLayout(layout)

        # First, ask to connect
        self.sigin_dialog = SignInDialog(self)
        self.sigin_dialog.user_signed_in.connect(self.set_user)

        # self._reset()
        self.set_user(token)

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
        self.set_user(None)

    def set_user(self, token: str):
        self.user_token = token  
        if token:  
            user = get_current_user(token, self.session)
            self.user = user
            self.username_label.setText(self.user.username)
            self.viewer.set_user(token, self.user)
            self.logger.log("Successfully logged as " + self.user.username, 2000)
            self.show()
        else:
            self.hide()
            self.logger.log("Waiting for login...")
            self.sigin_dialog.show()

    def logout(self):
        self.user_token = None
        self._reset()

    def reload(self):
        # TODO: refresh also the viewer
        self.browser.load()
        self.viewer.reset()

    def show(self):
        if not self.user_token:
            return
        super().show()

    def open_graph(self, graph: Graph):
        self.anatomist.show_labeled_graph(
            graph.get_mesh_path(), graph.get_path(), PointOfView.Left_to_Right
        )

    def set_status_message(self, msg:str, msecs=0):
        self.status_bar.showMessage(msg, msecs)

    def closeEvent(self):
        self.anatomist.close()