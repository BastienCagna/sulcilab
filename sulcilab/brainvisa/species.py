from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel


class DefaultSpecies(Enum):
    BABOON = ('Baboon', 'Babouin'),
    CHIMPENZEE = ('Chimpanzee', 'Chimpanzé'),
    GORILLA = ('Gorilla', 'Gorille'),
    HUMAN = ('Human', 'Humain'),
    MARMOUSET = ('Marmouset', 'Marmouset'),
    MACAQUE = ('Macaque', 'Macaque'),
    PONGO = ('Orang outan', 'Orang outan')

#############
# ORM Model #
#############
class Species(Base, SulciLabBase):
    __tablename__ = "species"

    fr_name = Column(String, unique=True, index=True)
    en_name = Column(String, unique=True, index=True)

##################
# Pydantic Model #
##################
class PSpeciesBase(BaseModel):
    fr_name: str
    en_name: str
class PSpecies(PSpeciesBase, SulciLabReadingModel):
    pass


###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PSpecies])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, Species, skip=skip, limit=limit)
