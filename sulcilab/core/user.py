from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from pydantic import BaseModel
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
from sulcilab.auth.auth_bearer import JWTBearer
from sulcilab.auth.auth_handler import decodeJWT, signJWT
from sulcilab.core.jwt import PJWT
import jwt
import typing
# if typing.TYPE_CHECKING:
# from sulcilab.brainvisa import LabelingSet

#############
# ORM Model #
#############
class User(Base, SulciLabBase):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # labelingsets = relationship("LabelingSet", back_populates="author")
    # sharedsets = relationship("SharedLabelingSet", back_populates="target")

###################
# Pydantic Models #
###################
class PSulciLabReadingModel(BaseModel):
    id: int
    # create_at: datetime
    # updated_at: datetime | None = None

    class Config:
        orm_mode = True


class PUserBase(BaseModel):
    email: str
    username: str

class PUserCreate(PUserBase):
    password: str

class PUserSignIn(BaseModel):
    email: str
    password: str
class PUser(PUserBase, SulciLabReadingModel):
    is_active: bool
    is_admin: bool
    # labelingsets: "List" = []
    # sharedsets: "List" = []
    # TODO: verify if it works properly without the type specification
    # labelingsets: "List[PLabelingSet]" = []
    # sharedsets: "List[PLabelingSet]" = []

# from sulcilab.brainvisa.labelingset import PLabelingSet
PUser.update_forward_refs()


###################
# CRUD Operations #
###################
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, item: PUserCreate):
    print("create", item.username, item.email, item.password)
    hashed_password = item.password + "notreallyhashed"
    db_user = User(
        email=item.email,
        username=item.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_admin_user(db: Session, item: PUserCreate):
    hashed_password = item.password + "notreallyhashed"
    db_user = User(
        email=item.email,
        username=item.username,
        hashed_password=hashed_password,
        is_admin=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# def get_user_token(db: Session, email: str, password: str):
#     hpass = password + "notreallyhashed"
#     try:
#         user = crud.get_one_by(db, User, email=email, hashed_password=hpass)
#         if user:
#             return signJWT(user)
#     except:
#         return None
def get_user_by_token(db: Session, token:str):
    # FIXME: should work with verify_signature to true
    # TODO: use .env to set the algorithms
    user_id = jwt.decode(token, algorithms="HS256", options={"verify_signature": False})['id']
    return crud.get(db, User, id=user_id)

##########
# Routes #
##########
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()
@router.post("/login", response_model=PJWT)
# async def login(user: PUserSignIn, db: Session = Depends(get_db)):
def login(user: PUserSignIn, db: Session = Depends(get_db)):
    hpass = user.password + "notreallyhashed"
    if '@' in user.email:
        user = crud.get_one_by(db, User, email=user.email, hashed_password=hpass)
    else:
        user = crud.get_one_by(db, User, username=user.email, hashed_password=hpass)
    if user:
        return signJWT(user)
    raise HTTPException(401, "Wrong credentials")

@router.get("/all", dependencies=[Depends(JWTBearer())], response_model=List[PUser])
def list_all(skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    users = crud.get_all(db, User, skip=skip, limit=limit)
    return users

@router.get("/me", dependencies=[Depends(JWTBearer())], response_model=PUser)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return get_user_by_token(db, token)

@router.post("/", response_model=PUser)
def create(user: PUserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_one_by(db, User, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="This Email already used.")
    return create_user(db, user) #crud.create_user(db, user)
