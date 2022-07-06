from pydantic import BaseModel
from datetime import datetime

import typing

if typing.TYPE_CHECKING:
    from sulcilab.brainvisa.schemas import LabelingSet
    
    
class SulciLabReadingModel(BaseModel):
    id: int
    # create_at: datetime
    # updated_at: datetime | None = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserSignIn(BaseModel):
    email: str
    password: str
class User(UserBase, SulciLabReadingModel):
    is_active: bool
    # labelingsets: list[LabelingSet] = []
    # sharedsets: list[LabelingSet] = []

class JWT(BaseModel):
    token: str
