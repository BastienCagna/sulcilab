from sulcilab.brainvisa.fold import PFold
from sulcilab.brainvisa.label import PLabel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Union
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel

#############
# ORM Model #
#############


class Labeling(Base, SulciLabBase):
    __tablename__ = "labelings"

    fold_id = Column(Integer, ForeignKey("folds.id"))
    fold = relationship("Fold", uselist=False)  # , back_populates="")
    label_id = Column(Integer, ForeignKey("labels.id"))
    label = relationship("Label", uselist=False)
    labelingset_id = Column(Integer, ForeignKey("labelingsets.id"))
    labelingset = relationship(
        "LabelingSet", back_populates="labelings", uselist=False)
    iterations = Column(Integer, default=0)
    rate = Column(Float, nullable=True)
    comment = Column(Text, nullable=True)

    def __str__(self):
        return 'Labeling#{}: {} {}'.format(self.id, self.fold.id, self.label.id)

##################
# Pydantic Model #
##################


class PLabelingBase(BaseModel):
    fold_id: int
    label_id: int
    labelingset_id: int
    rate: Union[float, None]
    comment: Union[str, None]


class PLabelingCreate(PLabelingBase):
    pass


class PLabeling(PLabelingBase, SulciLabReadingModel):
    fold: PFold
    label: PLabel
    iterations: int


PLabeling.update_forward_refs()

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()


@router.get("/all", response_model=List[PLabeling])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Labeling, skip=skip, limit=limit)
