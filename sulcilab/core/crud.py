from sqlalchemy.orm import Session
from sulcilab.core import models, schemas

from sqlalchemy.orm import Session

from sulcilab.core import models, schemas
from sulcilab.database import SulciLabBase


# class Controller:
#     model: SulciLabBase

#     def __init__(self, model:SulciLabBase) -> None:
#         self.model = model

#     def get_all(self, db: Session, skip: int = 0, limit: int = 100):
#         return db.query(self.model).offset(skip).limit(limit).all()

#     def get(self, db: Session, id: int):
#         return db.query(self.model).filter(self.model.id == id).first()

#     def create(self, db: Session, item):
#         db_item = models.BrainVisaDB(**item.dict())
#         db.add(db_item)
#         db.commit()
#         db.refresh(db_item)
#         return db_item

#     def update(self, db: Session, item):
#         raise NotImplementedError()

#     def delete(self, db: Session, id: int):
#         raise NotImplementedError()


def get_all(db: Session, model:SulciLabBase, skip: int = 0, limit: int = 100):
    if limit:
        return db.query(model).offset(skip).limit(limit).all()
    else:
        return db.query(model).offset(skip).all()

def get(db: Session, model:SulciLabBase, id: int):
    return db.query(model).filter(model.id == id).first()

def get_by(db: Session, model:SulciLabBase, **kwargs):
    query = db.query(model)
    for k, v in kwargs.items():
        query.filter(model[k] == v)
    return query.all()

def get_one_by(db: Session, model:SulciLabBase, **kwargs):
    query = db.query(model)
    for k, v in kwargs.items():
        query.filter(k == v)
    return query.first()

def create(db: Session, model:SulciLabBase, item: dict={}, **kwargs):
    for k, v in kwargs.items():
        item[k] = v
    db_item = model(**item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update(db: Session, model:SulciLabBase, item):
    raise NotImplementedError()

def delete(db: Session, model:SulciLabBase, id: int):
    raise NotImplementedError()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, item: schemas.UserCreate):
    hashed_password = item.password + "notreallyhashed"
    db_user = models.User(
        email=item.email,
        username=item.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
        
# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()

# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

# def get_user_by_username(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()

# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(
#         email=user.email, 
#         username=user.username, 
#         hashed_password=fake_hashed_password
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
