from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import ForwardRef, List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel

import typing
if typing.TYPE_CHECKING:
    from .subject import PSubjectBase

#############
# ORM Model #
#############
class Database(Base, SulciLabBase):
    __tablename__ = "databases"

    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    path = Column(Text)
    subjects = relationship("Subject", back_populates="database")


##################
# Pydantic Model #
##################
class PDatabaseBase(BaseModel):
    name: str
    description: str | None
    path: str
class PDatabaseCreate(PDatabaseBase):
    pass
PDatabase = ForwardRef('PSubjectBase')
class PDatabase(PDatabaseBase, SulciLabReadingModel):
    subjects: List['PSubjectBase'] = []

    class Config:
        orm_mode = True


###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PDatabase])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Database, skip=skip, limit=limit)
