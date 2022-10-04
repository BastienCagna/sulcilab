from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sulcilab.database import SulciLabBase, Base
from pydantic import BaseModel
from sulcilab.core.schemas import SulciLabReadingModel
# import secrets
from sqlalchemy.orm import Session
# from sulcilab.data import models, schemas
from fastapi import APIRouter, Depends, HTTPException
from sulcilab.core import crud
# from sulcilab.data.models import Color
# from sulcilab.data.schemas import Color as sColor
from sulcilab.database import SessionLocal, get_db
from sqlalchemy.orm import Session
from typing import List


#############
# ORM Model #
#############
DEFAULT_COLOR_NAME = "Unnamed"

class Color(Base, SulciLabBase):
    __tablename__ = "colors"

    name = Column(String, default=DEFAULT_COLOR_NAME, index=True)
    red = Column(Integer)
    green = Column(Integer)
    blue = Column(Integer)
    alpha = Column(Integer)

    def __str__(self):
        return 'Color#{} {}: {} {} {} {}'.format(
            self.id, self.name, self.red, self.green, self.blue, self.alpha)

    def to_hex(self, with_alpha=False):
        if with_alpha:
            return '#{:02x}{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue, self.alpha)
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)


##################
# Pydantic Model #
##################
class PColorBase(BaseModel):
    name: str
    red: int
    green: int
    blue: int
    alpha: int

class PColorCreate(PColorBase):
    pass

class PColor(PColorBase, SulciLabReadingModel):
    id: int


PColor.update_forward_refs()

###################
# CRUD Operations #
###################
# def get_color(db: Session, color_id: int):
#     return db.query(Color).filter(Color.id == color_id).first()

# def get_color_by_name(db: Session, name: str):
#     if name == DEFAULT_COLOR_NAME:
#         return None
#     return db.query(Color).filter(Color.name == name).first()

def get_color_by_values(db: Session, r:int, g:int, b:int):
    return db.query(Color).filter(Color.red == r).filter(Color.green == g).filter(Color.blue == b).first()


# def get_colors(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Color).offset(skip).limit(limit).all()

# def create_color(db: Session, color: PColorCreate):
#     db_item = Color(
#         name=color.name, red=color.red, green=color.green, blue=color.blue
#     )
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PColor])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_all(db, Color, skip=skip, limit=limit)
    return items