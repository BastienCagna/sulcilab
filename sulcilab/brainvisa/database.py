from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import ForwardRef, List, Union
from pydantic import BaseModel
from sulcilab.auth.auth_bearer import JWTBearer
from sulcilab.core.user import PUserBase, get_user_by_token
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
from sulcilab.utils.misc import sqlalchemy_to_pydantic_instance
from sulcilab.core.user import PUser, User, get_user_by_token, oauth2_scheme


#############
# ORM Model #
#############
class Database(Base, SulciLabBase):
    __tablename__ = "databases"

    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    path = Column(Text)
    subjects = relationship("Subject", back_populates="database")
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", uselist=False)
    is_public = Column(Boolean, default=False)
    sharings = relationship("DatabaseSharing", back_populates="database")


##################
# Pydantic Model #
##################
class PDatabaseBase(BaseModel):
    name: str
    description: Union[str, None]
    path: str
    owner: PUser
    is_public: bool = False
    sharings: List["PDatabaseSharingWithoutDatabase"] = []
    
    class Config:
        orm_mode = True
class PDatabaseCreate(PDatabaseBase):
    pass
class PDatabase(PDatabaseBase, SulciLabReadingModel):
    subjects: List['PSubject'] = []



from .subject import PSubject
from .databasesharing import PDatabaseSharingWithoutDatabase
PDatabaseBase.update_forward_refs()
PDatabaseCreate.update_forward_refs()
PDatabase.update_forward_refs()

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", dependencies=[Depends(JWTBearer())], response_model=List[PDatabase])
def index(skip: int = 0, limit: int = 100, only_mine=False, all=False, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_user_by_token(db, token)
    if all:
        if not cuser.is_admin:
            raise HTTPException(status_code=403, detail="Admin rights required.")
        else:
            dbs = crud.get_all(db, PDatabase)
    else:
        dbs = crud.get_by(db, Database, skip=skip, limit=limit, owner_id=cuser.id)
        dbs_ids = list(d.id for d in dbs)
        if not only_mine:
            for database in crud.get_by(db, Database, skip=skip, limit=limit, is_public=True):
                if not database.id in dbs_ids:
                    dbs.append(database)

    return sqlalchemy_to_pydantic_instance(dbs, PDatabase)
