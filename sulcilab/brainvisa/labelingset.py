from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Union
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base, SessionLocal, get_db
from sulcilab.core import crud
from sulcilab.core.schemas import SulciLabReadingModel


#############
# ORM Model #
#############
class LabelingSet(Base, SulciLabBase):
    __tablename__ = "labelingsets"

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="labelingsets", uselist=False)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    graph = relationship("Graph", uselist=False)
    nomenclature_id = Column(Integer, ForeignKey("nomenclatures.id"))
    nomenclature = relationship("Nomenclature", uselist=False)
    labelings = relationship("Labeling", back_populates="labelingset")
    
    # nomenclature = models.ForeignKey(Nomenclature, on_delete=models.CASCADE, default=None, related_name="labelingsets")
    # creation_date = models.DateTimeField(null=True)
    # commit_date = models.DateTimeField(null=True, blank=True)
    # name = models.CharField(max_length=150, null=True, blank=True)
    comment = Column(Text, nullable=True)

    def to_aims_graph(self):
        pass

##################
# Pydantic Model #
##################
class PLabelingSetBase(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    labelings: List["PLabeling"] = []
    comment: Union[str, None]
class PLabelingSetCreate(PLabelingSetBase):
    pass
class PLabelingSet(PLabelingSetBase, SulciLabReadingModel):
    author: 'PUserBase'
    graph: "PGraph"
    nomenclature: "PNomenclature"

class PLabelingSetShort(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    comment: Union[str, None]

from sulcilab.core.user import PUserBase
from .nomenclature import PNomenclature
from .graph import PGraph
from .labeling import PLabeling
PLabelingSetBase.update_forward_refs()
PLabelingSet.update_forward_refs()
###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PLabelingSet])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, LabelingSet, skip=skip, limit=limit)
