from fastapi import FastAPI
from fastapi.routing import APIRoute
from sulcilab.router import api_router
from sulcilab.database import Base, engine


Base.metadata.create_all(bind=engine)

def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
app.include_router(api_router) #, prefix=config.API_V1_STR)

