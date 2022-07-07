from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
import os.path as op
import enum

from .subject import PSubject
from .fold import PFold

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
        # db = BVDatabase(self.subject.database.path)
        # return db.get_from_template(
        #     'morphologist_mesh',
        #     center=self.analysis.subject.center,
        #     subject=self.analysis.subject.name,
        #     acquisition=self.analysis.subject.acquisition,
        #     analysis=self.analysis.analysis,
        #     hemi=self.hemisphere,
        #     type=type
        # )[0]
        v_path = op.join(self.subject.database.path, self.subject.center, "t1mri", self.acquisition, self.analysis, "folds", self.version)
        if not self.session:
            return op.join(v_path, "{}{}.arg".format(self.hemisphere, self.subject.name))
        else:
            return op.join(v_path, self.session, "{}{}_{}.arg".format(self.hemisphere, self.subject.name, self.session))


##################
# Pydantic Model #
##################
class PGraphBase(BaseModel):
    subject_id: int
    acquisition: str
    analysis: str
    hemisphere: str
    version: str
    session: str | None
class PGraphCreate(PGraphBase):
    pass
class PGraph(PGraphBase, SulciLabReadingModel):
    subject: PSubject
    folds: list[PFold]

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PGraph])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Graph, skip=skip, limit=limit)
