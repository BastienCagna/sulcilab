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
    from .label import PLabel


#############
# ORM Model #
#############
class Nomenclature(Base, SulciLabBase):
    __tablename__ = "nomenclatures"

    name = Column(String, unique=True)
    default = Column(Boolean, default=False) # replace this by a value in settings and provide the suited controller
    labels = relationship("Label", back_populates="nomenclature")

    def __str__(self) -> str:
        return "Nomenclature#{}: {}".format(self.id, self.name)



##################
# Pydantic Model #
##################
class PNomenclature(BaseModel):
    name: str
    default: bool
    labels: list['PLabel']

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PNomenclature])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db,  Nomenclature, skip=skip, limit=limit)
