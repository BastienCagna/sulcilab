from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from sulcilab.brainvisa.sharedlabelingset import SharingMode
from sulcilab.database import SulciLabBase, Base
from sulcilab.core.schemas import SulciLabReadingModel
from sulcilab.core.user import PUser


#############
# ORM Model #
#############
class DatabaseSharing(Base, SulciLabBase):
    __tablename__ = "databasesharings"

    database_id = Column(Integer, ForeignKey("databases.id"))
    database = relationship("Database", uselist=False)
    target_id = Column(Integer, ForeignKey("users.id"))
    target = relationship("User", uselist=False)
    mode = Column(Enum(SharingMode))


##################
# Pydantic Model #
##################
class PDatabaseSharingBase(BaseModel):
    database: 'PDatabase'
    target: 'PUser'
    mode: int
class PDatabaseSharingCreate(PDatabaseSharingBase):
    pass
class PDatabaseSharing(PDatabaseSharingBase, SulciLabReadingModel):
    pass

from sulcilab.core.user import PUser
from .database import PDatabase
PDatabaseSharing.update_forward_refs()

###################
# CRUD Operations #
###################


