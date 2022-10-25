from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import get_db
from sulcilab.core.schemas import SulciLabReadingModel


#############
# ORM Model #
#############
class Subject(Base, SulciLabBase):
    __tablename__ = "subjects"

    database_id = Column(Integer, ForeignKey("databases.id"))
    database = relationship("Database", back_populates="subjects")
    center = Column(String)
    name = Column(String)
    graphs = relationship("Graph", back_populates="subject")
    species_id = Column(Integer, ForeignKey("species.id"))
    species = relationship("Species")

    def __str__(self):
        return "Subject#{}: {}".format(self.id, self.name)

    def get_one_graph(self, hemisphere=None, acquisistion=None, analysis=None, version=None, session=None):
        """ Return the first graph that match the requirements or None if any graph matches. """
        for g in self.graphs:
            if hemisphere is not None and hemisphere != g.hemisphere.value:
                continue
            if acquisistion is not None and acquisistion != g.acquisition:
                continue
            if analysis is not None and acquisistion != g.analysis:
                continue
            if version is not None and acquisistion != g.version:
                continue
            if session is not None and acquisistion != g.session:
                continue
            return g
        return None


##################
# Pydantic Model #
##################
class PSubjectBase(BaseModel):
    database_id: int
    center: str
    name: str
    species: "PSpecies"
    graphs: List = []
class PSubjectCreate(PSubjectBase):
    pass
class PSubject(PSubjectBase, SulciLabReadingModel):
    database: "PDatabase"


from .database import PDatabase
from .species import PSpecies
PSubject.update_forward_refs()
PSubjectBase.update_forward_refs()
###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PSubject])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Subject, skip=skip, limit=limit)
