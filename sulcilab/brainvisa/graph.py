from glob import glob
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Union
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
import os.path as op
import enum
import ujson

import nibabel as nb
# from .subject import PSubject
# from .fold import PFold

class GraphVersion(enum.Enum):
    V30 = "3.0"
    V31 = "3.1"
    V32 = "3.2"
    V33 = "3.3"

class Hemisphere(enum.Enum):
    left = "L"
    right = "R"

#############
# ORM Model #
#############
class Graph(Base, SulciLabBase):
    __tablename__ = "graphs"

    subject = relationship("Subject", back_populates="graphs")
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    acquisition = Column(String)
    analysis = Column(String)
    hemisphere = Column(Enum(Hemisphere))
    version = Column(Enum(GraphVersion))
    session = Column(String, nullable=True)
    folds = relationship("Fold", back_populates="graph")

    def get_mesh_path(self, type="white") -> str:
        v_path = op.join(self.subject.database.path, self.subject.center if self.subject.center else "*", self.subject.name, "t1mri", self.acquisition, self.analysis, "segmentation", "mesh")
        temp = op.join(v_path, f"{self.subject.name}_{self.hemisphere.value}{type}.gii")
        return glob(temp)[0]

    def get_path(self):
        v_path = op.join(self.subject.database.path, self.subject.center if self.subject.center else "*", self.subject.name, "t1mri", self.acquisition, self.analysis, "folds", self.version.value)
        if not self.session:
            tmp = op.join(v_path, "{}{}.arg".format(self.hemisphere.value, self.subject.name))
        else:
            tmp = op.join(v_path, self.session, "{}{}_{}.arg".format(self.hemisphere.value, self.subject.name, self.session))
        return glob(tmp)[0]

    def get_folds_meshes_path(self):
        data_path = self.get_path()[:-4] + '.data'
        return op.join(data_path, "aims_Tmtktri.gii")

    def load_mesh(self, type="hemi"):
        gii = nb.load(self.get_mesh_path(type=type))
        return {
            'type': type,
            'vertices': gii.darrays[0].data.tolist(),
            'triangles': gii.darrays[1].data.tolist()
        }

    def load_folds_meshes(self):
        gii = nb.load(self.get_folds_meshes_path())
        data = []
        for f in range(0, len(gii.darrays), 2):
            data.append({
                'type': 'fold',
                'vertices': gii.darrays[f].data.tolist(),
                'triangles': gii.darrays[f+1].data.tolist()
            })
        return data

##################
# Pydantic Model #
##################
class PGraphBase(BaseModel):
    subject_id: int
    acquisition: str
    analysis: str
    hemisphere: Union[str, Hemisphere]
    version: Union[str, GraphVersion]
    session: Union[str, None]
class PGraphCreate(PGraphBase):
    pass
class PGraph(PGraphBase, SulciLabReadingModel):
    subject: "PSubjectBase"

class PGraphFull(PGraph, SulciLabReadingModel):
    folds: "List[PFold]"


class PMeshData(BaseModel):
    type: str
    triangles: list
    vertices: list

from .subject import PSubjectBase
from .fold import PFold
PGraph.update_forward_refs()
PSubjectBase.update_forward_refs()
###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PGraph])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all(db, Graph, skip=skip, limit=limit)


@router.get("/meshdata")
def get_mesh_data(graph_id: int, mtype:str="white", db: Session = Depends(get_db)):
    graph = crud.get(db, Graph, graph_id)
    # src: https://stackoverflow.com/questions/73564771/fastapi-is-very-slow-in-returning-a-large-amount-of-json-data
    return Response(ujson.dumps(graph.load(mtype)), media_type="application/json")