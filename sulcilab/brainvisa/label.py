from importlib_metadata import metadata
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text, Enum, Float
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
nomLabelAssociationTable = Table(
    "nomlabel",
    Base.metadata,
    Column("nomenclature", ForeignKey("nomenclatures.id")),
    Column("label", ForeignKey("labels.id"))
)

class Label(Base, SulciLabBase):
    __tablename__ = "labels"

    shortname = Column(String)
    fr_name = Column(String)
    en_name = Column(String)
    fr_description = Column(Text)
    en_description = Column(Text)
    parent_id = Column(Integer, ForeignKey("labels.id"))
    parent = relationship("Label", uselist=False) #, back_populates="children")
    color_id = Column(Integer, ForeignKey("colors.id"))
    color = relationship("Color")
    # parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    # color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    left = Column(Boolean, default=False)
    right = Column(Boolean, default=False)
    link = Column(Text)

    #nomenclatures_id = Column(Integer, ForeignKey("nomenclatures.id"))
    #nomenclatures = relationship("Nomenclature", secondary=nomLabelAssociationTable, backref="labels", uselist=True)

    def __str__(self) -> str:
        return "Label{}: {}".format(self.id, self.shortname)
    

##################
# Pydantic Model #
##################
class PLabelBase(BaseModel):
    shortname: str
    fr_name: Union[str, None]
    en_name: Union[str, None]
    fr_description: Union[str, None]
    en_description: Union[str, None]
    parent_id: Union[int, None]
    color_id: int
    # nomenclature_id: int
    left: bool
    right: bool
    link: Union[str, None]
class PLabelCreate(PLabelBase):
    pass
class PLabel(PLabelBase, SulciLabReadingModel):
    parent: Union['PLabel', None]
    # nomenclature: 'PNomenclature'
    color: 'PColor'

# from .nomenclature import PNomenclature
from sulcilab.data.color import PColor
PLabel.update_forward_refs()

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

