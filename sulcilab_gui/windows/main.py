import typing
from uuid import uuid4
# from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import QtGui
import PyQt5.QtWidgets as qtw
from warnings import warn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sulcilab.brainvisa.labelingset import PLabelingSetShort
from sulcilab.brainvisa.species import PSpecies


from sulcilab_gui.dialogs import SignInDialog
from sulcilab_gui.widgets import CollapsibleBox
from sulcilab.database import SessionLocal
from sulcilab.brainvisa.database import read, PDatabase
from sulcilab.brainvisa.subject import PSubject, PSubjectBase, Subject
from sulcilab.brainvisa.graph import Graph
from sulcilab.core.user import get_current_user, User, PUser
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



class SlApi:
    def __init__(self):
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        self.session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def signin(self, username, password):
        pass

    def get_current_user(self):
        pass

    def get_databases(self):
        pass

# class SubjectWidget(CollapsibleBox):
#     def __init__(self, parent, subject:PSubject):
#         # super(CollapsibleBox, self).__init__(subject.name, parent)
#         super().__init__(subject.name, parent)
#         self.subject = subject

#         layout = qtw.QVBoxLayout(self)
#         layout.addWidget(qtw.QLabel("Espèce: " + (subject.species.fr_name if subject.species else "N.C"), self))
#         layout.addWidget(qtw.QLabel("Centre: " + (subject.center if subject.center else "N.C"), self))
#         for graph in subject.graphs:
#             layout.addWidget(qtw.QLabel(str(graph.version) + " | " +str(graph.hemisphere)))
#         self.setContentLayout(layout)
#         # for lset in subject.l
#         # self.subject_name = qtw.QLabel(subject.name, self)        

#         # self.layout.addWidget(self.subject_name)
#         # self.setLayout(self.layout)

# class DatabaseExplorerWidget(QWidget):
#     def __init__(self, parent, database:PDatabase):
#         super(QWidget, self).__init__(parent)
#         self.layout = qtw.QVBoxLayout(self)
#         self.database = database

#         for subject in self.database.subjects:
#             self.layout.addWidget(SubjectWidget(self, subject))
#         self.setLayout(self.layout)
    
# class DatabasesExplorerTabsWidget(QWidget):
    
#     def __init__(self, parent):
#         super(QWidget, self).__init__(parent)
#         self.layout = qtw.QVBoxLayout(self)
        
#         self.tabs = qtw.QTabWidget()
#         self.layout.addWidget(self.tabs)
#         self.setLayout(self.layout)
#         self.load()
    
#     def load(self):
#         self.databases = read(db=SessionLocal())
#         for i in range(self.tabs.count()):
#             self.tabs.removeTab(i)
#         for db in self.databases:
#             tab = DatabaseExplorerWidget(self, db)
#             self.tabs.addTab(tab, db.name)

class BrowserWidget(qtw.QWidget):
    subject_selected = pyqtSignal(PSubjectBase, name="SubjectSelected")

    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
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
        databases = read(db=SessionLocal())
        self.db_listitems.clear()
        self.sub_listitems.clear()
        self.databases = []
        for db in databases:
            self.db_listitems.addItem(db.name)
            self.databases.append(PDatabase(
                id=db.id,
                name=db.name,
                description=db.description,
                path=db.path,
                subjects=list(PSubjectBase(
                    id=s.id,
                    database_id=db.id,
                    center=s.center,
                    name=s.name,
                    species=PSpecies(id=0, fr_name="N.C", en_name="N.C")
                ) for s in db.subjects)
            ))

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


class SubjectHemisphereControlsWidget(qtw.QWidget):
    open_graph = pyqtSignal(Graph, name="OpenGraph")

    def __init__(self, h, parent = None):
        super(qtw.QWidget, self).__init__(parent)
        if h not in ['L', 'R']:
            raise ValueError(f'Hemisphere is expected to be "L" or "R" not "{str(h)}".')
        self.hemi = h
        self.hemisphere = "Left" if h == "L" else "Right"
        self._create_ui()
        self.reset()

    def _create_ui(self):
        layout = qtw.QVBoxLayout(self)
        self.title_label = qtw.QLabel(self.hemisphere + " hemisphere", self)
        self.title_label.setFont(QtGui.QFont('Arial', 10, weight=QtGui.QFont.Bold))
        self.open_graph_btn = qtw.QPushButton("Open graph", self)
        self.open_graph_btn.clicked.connect(self.send_open_graph)

        layout.addWidget(self.title_label)
        layout.addWidget(self.open_graph_btn)
        self.setLayout(layout)

    def reset(self):
        self.user = None
        self.subject = None
        self.graph = None
        self.open_graph_btn.setDisabled(True)

    def set_user(self, user:str):
        """ Set tje JWT token to allow the widget to query the database """
        self.user = user

    def set_subject(self, subject):
        self.subject = subject

        if not self.user:
            raise RuntimeError("User isn't set. Cannot access to the database.")
        #     # src: https://www.tutorialspoint.com/pyqt/pyqt_qmessagebox.htm
        #     msg = qtw.QMessageBox()
        #     msg.setIcon(qtw.QMessageBox.Warning)
        #     msg.setText("User not set. Cannot access to the database.")
        #     msg.setWindowTitle("User token not set")
        #     msg.setStandardButtons(qtw.QMessageBox.Close)
        #     msg.exec_()
        # else:
        for graph in self.subject.graphs:
            if graph.hemisphere.value == self.hemi:
                self.graph = graph
                self.open_graph_btn.setDisabled(False)

    def send_open_graph(self):
        self.open_graph.emit(self.graph)


class SubjectWidget(qtw.QWidget):
    def __init__(self, parent = None):
        super(qtw.QWidget, self).__init__(parent)
        self._create_ui()
        self.reset()

    def _create_ui(self):
        layout = qtw.QVBoxLayout(self)

        self.name_label = qtw.QLabel(self)
        self.name_label.setFont(QtGui.QFont('Arial', 14, weight=QtGui.QFont.Bold))
        self.species_label = qtw.QLabel(self)
        self.center_label = qtw.QLabel(self)

        verticalSpacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        self.left_controls = SubjectHemisphereControlsWidget("L", self)
        self.right_controls = SubjectHemisphereControlsWidget("R", self)

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

    def set_user(self, user:User):
        self.user = user
        self.left_controls.set_user(user)
        self.right_controls.set_user(user)

    def set_subject(self, subject:Subject):
        self.current_subject = subject
        self.left_controls.set_subject(subject)
        self.right_controls.set_subject(subject)

        self.name_label.setText(subject.database.name + "/ " + subject.name)
        self.species_label.setText("Species: " + (subject.species.fr_name if subject.species else 'N.C'))
        self.center_label.setText(f"Center: {subject.center}")


class MainWindow (qtw.QMainWindow):
    _anatomist_instance = None

    def __init__(self, app_name:str, token=None) -> None:
        super().__init__()
        self.resize(600, 800)
        self.setWindowTitle(app_name)
        self._create_actions()
        # self._create_menu_bar()
        self._create_toolbar()

        self.browser = BrowserWidget(self)
        self.dock = qtw.QDockWidget("Browser")
        self.dock.setWidget(self.browser)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.viewer = SubjectWidget(self)
        self.browser.subject_selected.connect(self.viewer.set_subject)
        self.viewer.left_controls.open_graph.connect(self.open_graph)
        self.viewer.right_controls.open_graph.connect(self.open_graph)
        self.setCentralWidget(self.viewer)
        # layout = qtw.QHBoxLayout(self)
        # layout.addWidget(self.browser)
        # self.setLayout(layout)

        # First, ask to connect
        self.sigin_dialog = SignInDialog(self)
        self.sigin_dialog.user_signed_in.connect(self.set_user)

        self.anatomist = Anatomist()

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
        self.set_user(None)

    def set_user(self, token: str):
        self.user_token = token  
        if token:   
            print(token)   
            user = get_current_user(token, SessionLocal())
            self.user = PUser(
                id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                is_admin=user.is_admin,
                labelingsets=list(PLabelingSetShort(
                    id=s.id, author_id=s.author_id, graph_id=s.graph_id,
                    nomenclature_id=s.nomenclature_id, comment=s.comment
                ) for s in user.labelingsets),
                # TODO: to be completed
                sharedsets=list()
            )
            #username = "Bastien" #jwt.decode(token, algorithms="HS256", options={"verify_signature": False})['username']
            self.username_label.setText("User: " + self.user.username)
            self.viewer.set_user(self.user)
            self.show()
        else:
            self.hide()
            self.sigin_dialog.show()
            # self.set_user_token("fake_token")

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


class Anatomist:
    def __init__(self):
        self._reset()

    def _check_instance(self):
         if self._instance is None:
            self._instance = None # ana.Anatomist()

    def _reset(self):
        self._instance = None
        self._objects = {}
        self._windows = {}
        self.hie = None

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
