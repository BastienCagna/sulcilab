from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel


import typing
if typing.TYPE_CHECKING:
    from .graph import PGraph

#############
# ORM Model #
#############
class Fold(Base, SulciLabBase):
    __tablename__ = "folds"

    graph_id = Column(Integer, ForeignKey("graphs.id"))
    graph = relationship("Graph", back_populates="folds")
    vertex = Column(Integer)


##################
# Pydantic Model #
##################
class PFoldBase(BaseModel):
    graph_id: int
    vertex: int
class PFoldCreate(PFoldBase):
    pass
class PFold(PFoldBase, SulciLabReadingModel):
    # graph: 'PGraph'
    pass

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PFold])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Fold, skip=skip, limit=limit)
