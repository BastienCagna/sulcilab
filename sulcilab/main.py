from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from os import makedirs, system
import os.path as op
import json

from sulcilab.core import models, crud, schemas
from sulcilab.database import SessionLocal, engine
from sulcilab.data import schemas as dschema
from sulcilab.data import models as dmodels
import sulcilab.brainvisa.schemas as bschema
import sulcilab.brainvisa.models as bmodels
from sulcilab.auth.auth_bearer import JWTBearer
from sulcilab.auth.auth_handler import signJWT, get_current_user
from .utils import BUILD_PATH

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

##########
# User
##########
@app.post("/user/login", response_model=schemas.JWT)
async def user_login(user: schemas.UserSignIn, db: Session = Depends(get_db)):
    hpass = user.password + "notreallyhashed"
    try:
        user = crud.get_one_by(db, models.User, email=user.email, hashed_password=hpass)
        if user:
            return signJWT(user)
    except:
        raise HTTPException(401, "Wrong credentials")

@app.post("/user", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_one_by(db, models.User, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="This Email already used.")
    return crud.create_user(db, user)

@app.get("/users", dependencies=[Depends(JWTBearer())], response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    users = crud.get_all(db, models.User, skip=skip, limit=limit)
    return users


#######
# Colors
###########
@app.get("/colors", response_model=list[dschema.Color])
def read_colors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_all(db, dmodels.Color, skip=skip, limit=limit)
    return items


#####
# Nomenclature
########



# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items





@app.on_event("startup")
def startup():
    print("Exporting the OpenAPI schema specifications")
    makedirs(BUILD_PATH, exist_ok=True)
    with open(op.join(BUILD_PATH, "openapi.json"), 'w+') as afp:
        json.dump(app.openapi(), afp, indent=4)

    print("Regenerate the Typescript API")
    system("npx @nll/api-codegen-ts")