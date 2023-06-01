from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sulcilab.auth.auth_bearer import JWTBearer
from sulcilab.database import SulciLabBase, Base
from sulcilab.core import crud
from sulcilab.database import SessionLocal, get_db
from sulcilab.core.schemas import SulciLabReadingModel
from sulcilab.core.user import PUser, User, get_current_user, get_user_by_token, oauth2_scheme
import enum


class SharingMode(enum.Enum):
    READONLY = 0
    COMMENT = 1
    EDIT = 2

#############
# ORM Model #
#############
class SharedLabelingSet(Base, SulciLabBase):
    __tablename__ = "sharedlabelingsets"

    labelingset_id = Column(Integer, ForeignKey("labelingsets.id"))
    labelingset = relationship("LabelingSet", uselist=False)
    target_id = Column(Integer, ForeignKey("users.id"))
    target = relationship("User", uselist=False)
    mode = Column(Enum(SharingMode))


##################
# Pydantic Model #
##################
class PSharedLabelingSetBase(BaseModel):
    labelingset: 'PLabelingSet'
    target: 'PUser'
    mode: int
class PSharedLabelingSetCreate(PSharedLabelingSetBase):
    pass
class PSharedLabelingSetWithoutLabelingSet(SulciLabReadingModel):
    target: 'PUser'
    mode: int
class PSharedLabelingSet(PSharedLabelingSetBase, SulciLabReadingModel):
    pass

from sulcilab.core.user import PUser
from .labelingset import LabelingSet, PLabelingSet
PSharedLabelingSetBase.update_forward_refs()
PSharedLabelingSetCreate.update_forward_refs()
PSharedLabelingSetWithoutLabelingSet.update_forward_refs()
PSharedLabelingSet.update_forward_refs()
###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", dependencies=[Depends(JWTBearer())], response_model=List[PSharedLabelingSet])
def read(skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser: PUser = get_user_by_token(db, token)
    if not cuser.is_admin:
        # TODO: use decorator for this verification
        raise HTTPException(status_code=403, detail="Admin rights required.")
    return crud.get_all(db, SharedLabelingSet, skip=skip, limit=limit)


# Get users to ho the labeling set is shared
@router.get("/users", dependencies=[Depends(JWTBearer())], response_model=List[PUser])
def sharing_recipient(lset_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_user_by_token(db, token)
    recipient_sharings = crud.get_by(db, SharedLabelingSet, labelingset_id=lset_id)
    ruser_ids = list(sh.target_id for sh in recipient_sharings)
    if not cuser.is_admin:
        lset = crud.get(db, LabelingSet, lset_id)
        if not cuser.id in ruser_ids and lset.author_id != cuser.id:
            # TODO: use decorator for this verification
            raise HTTPException(status_code=403, detail="Authorship or admin rights required.")
    
    return list(sh.target for sh in recipient_sharings)

# Create a new sharing
@router.post("/add", dependencies=[Depends(JWTBearer())], response_model=PSharedLabelingSet)
def create(lset_id: int, user_id:int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_current_user(db, token)
    lset = crud.get_by(db, SharedLabelingSet, labelingset_id=lset_id)
    mode = SharingMode.READONLY
    if mode < 0 or mode > 2:
        raise HTTPException(status_code=400)
    
    if not cuser.is_admin and cuser.id != lset.author_id:
        # TODO: use decorator for this verification
        raise HTTPException(status_code=403, detail="Authorship or admin rights required.")

    if lset.author_id == user_id:
        raise HTTPException(status_code=400, detail="The target user is the author.")
    
    existing = crud.get_one_by(db, SharedLabelingSet, labelingset_id=lset_id, target_id=user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Already existing sharing")

    return crud.create(db, SharedLabelingSet,
        labelingset_id=lset_id,
        target_id=user_id,
        mode=mode
    )


@router.delete("/del", dependencies=[Depends(JWTBearer())])
def delete_labelingset(sharing_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser: PUser = get_user_by_token(db, token)
    
    sharing = crud.get(db, SharedLabelingSet, sharing_id)

    if sharing is None:
        raise HTTPException(status_code=404)
    if sharing.labelingset.author_id != cuser.id and sharing.target_id != cuser.id and not cuser.is_admin:
        raise HTTPException(status_code=403, detail="Authorship or admin rights requested.")
    
    crud.delete(db, SharedLabelingSet, sharing.id)
    return None

# Get the shared labelingsets
@router.get("/labelingsetsof", dependencies=[Depends(JWTBearer())], response_model=List[PLabelingSet])
def labelingsets_shared_with(target_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_current_user(db, token)
    if not cuser.is_admin and target_id != cuser:
        raise HTTPException(status_code=403, detail="Ownership or admin rights requested.")
    lsets = []
    for sharing in crud.get_by(db, SharedLabelingSet, target_id=target_id):
        lsets.append(sharing.labelingset)
    return lsets


@router.post("/update_several", dependencies=[Depends(JWTBearer())])
def update_sharings(lset_id:int, user_ids:List[int], token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_user_by_token(db, token)
    # Get true item to verify authorship
    lset = crud.get(db, LabelingSet, lset_id)

    if lset is None:
        raise HTTPException(status_code=404)
    if lset.author_id != cuser.id and not cuser.is_admin:
        raise HTTPException(status_code=403, detail="Authorship or admin rights required.")

    # Remove sharings if necessary
    original_sharings = crud.get_by(db, SharedLabelingSet, labelingset_id=lset.id)
    always_present_targets = []
    for sh in original_sharings:
        if sh.target_id in user_ids:
            always_present_targets.append(sh.target_id)
        else:
            crud.delete(db, SharedLabelingSet, sh.id)
    
    # Add new ones
    for uid in user_ids:
        if not uid in always_present_targets:
            crud.create(db, SharedLabelingSet,
                labelingset_id=lset_id,
                target_id=uid,
                mode=SharingMode.READONLY
            )
    
