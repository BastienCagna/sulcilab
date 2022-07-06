from sqlalchemy.orm import Session

from sulcilab.brainvisa import models, schemas
from sulcilab.database import SulciLabBase

class Controller:
    model: SulciLabBase

    def __init__(self, model:SulciLabBase) -> None:
        self.model = model

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).offset(skip).limit(limit).all()

    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, item):
        db_item = models.BrainVisaDB(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update(self, db: Session, item):
        raise NotImplementedError()

    def delete(self, db: Session, id: int):
        raise NotImplementedError()

# def get_color_by_name(db: Session, name: str):
#     if name == models.DEFAULT_COLOR_NAME:
#         return None
#     return db.query(models.Color).filter(models.Color.name == name).first()

# def get_color_by_values(db: Session, r:int, g:int, b:int):
#     return db.query(models.Color).filter(models.Color.red == r).filter(models.Color.green == g).filter(models.Color.blue == b).first()

# def create_color(db: Session, color: schemas.ColorCreate):
#     db_item = models.Color(
#         name=color.name, red=color.red, green=color.green, blue=color.blue
#     )
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item

####################
# DATABASES
####################
# def get_database(db: Session, id: int):
#     return db.query(models.BrainVisaDB).filter(models.BrainVisaDB.id == id).first()

# def get_databases(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.BrainVisaDB).offset(skip).limit(limit).all()

# def create_color(db: Session, item: schemas.BrainVisaDBCreate):
#     db_item = models.BrainVisaDB(
#         name=item.name, description=item.description, path=item.path
#     )
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item

####################
# SPECIES
####################


####################
# SUBJECTS
####################


####################
# GRAPHS
####################


####################
# FOLDS
####################


####################
# NOMENCLATURES
####################


####################
# LABELS
####################


####################
# LABELINGS
####################


####################
# LABELINGSETS
####################

