from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
from .nomenclature import PNomenclature
from sulcilab.data.color import PColor

#############
# ORM Model #
#############
class Label(Base, SulciLabBase):
    __tablename__ = "labels"

    shortname = Column(String)
    fr_name = Column(String)
    en_name = Column(String)
    fr_description = Column(Text)
    en_description = Column(Text)
    parent_id = Column(Integer, ForeignKey("labels.id"))
    parent = relationship("Label") #, back_populates="children")
    color_id = Column(Integer, ForeignKey("colors.id"))
    color = relationship("Color")
    # parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    # color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    left = Column(Boolean, default=False)
    right = Column(Boolean, default=False)
    link = Column(Text)

    nomenclature_id = Column(Integer, ForeignKey("nomenclatures.id"))
    nomenclature = relationship("Nomenclature", back_populates="labels", uselist=False)
    #nomenclatures = models.ManyToManyField(Nomenclature(), related_name="labels")

    def __str__(self) -> str:
        return "Label{}: {}".format(self.id, self.shortname)



##################
# Pydantic Model #
##################
class PLabelBase(BaseModel):
    shortname: str
    fr_name: str
    en_name: str
    fr_description: str
    en_description: str
    parent_id: int | None
    color_id: int
    nomenclature_id: int
    left: bool
    right: bool
    link: str
class PLabelCreate(PLabelBase):
    pass
class PLabel(PLabelBase, SulciLabReadingModel):
    parent: 'PLabel'
    color: PColor
    nomenclature: PNomenclature

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PLabel])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Label, skip=skip, limit=limit)
