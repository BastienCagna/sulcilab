from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
import enum


class SharingMode(enum.Enum):
    READONLY = 0
    COMMENT = 1
    EDIT = 2

#############
# ORM Model #
#############
class SharedLabelingSet(Base, SulciLabBase):
    __tablename__ = "sharedlabelingsets"

    labelingset_id = Column(Integer, ForeignKey("labelingsets.id"))
    labelingset = relationship("LabelingSet", uselist=False)
    target_id = Column(Integer, ForeignKey("users.id"))
    target = relationship("User", back_populates="sharedsets", uselist=False)
    mode = Column(Enum(SharingMode))


##################
# Pydantic Model #
##################
class PSharedLabelingSetBase(BaseModel):
    labelingset: 'PLabelingSet'
    target: 'PUser'
    mode: int
class PSharedLabelingSetCreate(PSharedLabelingSetBase):
    pass
class PSharedLabelingSet(PSharedLabelingSetBase, SulciLabReadingModel):
    pass

from sulcilab.core.user import PUser
from .labelingset import PLabelingSet
PSharedLabelingSet.update_forward_refs()
###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PSharedLabelingSet])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, SharedLabelingSet, skip=skip, limit=limit)