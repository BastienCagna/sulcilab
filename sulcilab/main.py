from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from .router import api_router
from .database import Base, engine


Base.metadata.create_all(bind=engine)

def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
app.include_router(api_router) #, prefix=config.API_V1_STR)


# @app.on_event("startup")
# def startup():
