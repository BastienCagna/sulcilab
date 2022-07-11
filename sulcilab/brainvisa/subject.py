from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import get_db
from sulcilab.core.schemas import SulciLabReadingModel
from .database import PDatabase
from .species import PSpecies


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


##################
# Pydantic Model #
##################
class PSubjectBase(BaseModel):
    database_id: int
    center: str
    name: str
    species: PSpecies
class PSubjectCreate(PSubjectBase):
    pass
class PSubject(PSubjectBase, SulciLabReadingModel):
    database: PDatabase


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
