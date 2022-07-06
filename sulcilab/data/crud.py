import secrets
from sqlalchemy.orm import Session
from sulcilab.data import models, schemas


def get_color(db: Session, color_id: int):
    return db.query(models.Color).filter(models.Color.id == color_id).first()

def get_color_by_name(db: Session, name: str):
    if name == models.DEFAULT_COLOR_NAME:
        return None
    return db.query(models.Color).filter(models.Color.name == name).first()

def get_color_by_values(db: Session, r:int, g:int, b:int):
    return db.query(models.Color).filter(models.Color.red == r).filter(models.Color.green == g).filter(models.Color.blue == b).first()


def get_colors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Color).offset(skip).limit(limit).all()

def create_color(db: Session, color: schemas.ColorCreate):
    db_item = models.Color(
        name=color.name, red=color.red, green=color.green, blue=color.blue
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
