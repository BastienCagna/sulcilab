from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QDialog, QLineEdit, QPushButton, QLabel
import PyQt5.QtWidgets as qtw
import fastapi
from sqlalchemy.orm import Session
from sulcilab.brainvisa import labelingset
from sulcilab.brainvisa.graph import Graph
from sulcilab.brainvisa.nomenclature import PNomenclature, get_all_nomenclatures
from sulcilab.core.user import User


class NewLabelingSetDialog(QDialog):
    user_signed_in = pyqtSignal(str, name="UserSignedIn")

    def __init__(self, user: User, graph: Graph, token:str, db:Session, parent=None):
        super(QDialog, self).__init__(parent)
        self.user = user
        self.graph = graph
        self.database = db
        self.token = token
        self.labeling_set = None

        layout = qtw.QVBoxLayout(self)

        layout.addWidget(QLabel("Select a nomenclature:"))
        self.nomenclature_combo = qtw.QComboBox(self)
        nomenclatures: List[PNomenclature] = get_all_nomenclatures(db=self.database)
        for nom in nomenclatures:
            self.nomenclature_combo.addItem(nom.name, nom)
        layout.addWidget(self.nomenclature_combo)

        sub_layout = qtw.QVBoxLayout(self)
        self.ok_btn = QPushButton('Ok', self)
        self.ok_btn.clicked.connect(self.new_labelingset)
        sub_layout.addWidget(self.ok_btn)
        self.cancel_btn = QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.reject)
        sub_layout.addWidget(self.cancel_btn)
        layout.addLayout(sub_layout)

        self.message = QLabel(self)
        layout.addWidget(self.message)

    def new_labelingset(self):
        lset = labelingset.PLabelingSetCreate(
            author_id=self.user.id,
            graph_id=self.graph.id,
            nomenclature_id=self.nomenclature_combo.currentData().id,
        )

        try:
            lset = labelingset.new_labelingset(lset, self.token, self.database)
        except fastapi.exceptions.HTTPException:
            self.message.setText("An error occured")
        else:
            self.labeling_set = lset
            self.accept()

