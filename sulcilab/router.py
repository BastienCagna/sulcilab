# app/api/api_v1/api.py
from fastapi import APIRouter

# from app.api.api_v1.endpoints import items, login, users, utils
from sulcilab.data import color
from sulcilab.core import user
from sulcilab.brainvisa import database, fold, graph, label, labeling, labelingset, nomenclature, sharedlabelingset, species, subject

api_router = APIRouter()
# api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, tags=["Users"], prefix="/user")

api_router.include_router(color.router, tags=["Colors"], prefix="/color")

# api_router.include_router(database.router,n tags=["databases"], prefix="/database")
api_router.include_router(fold.router, tags=["folds"], prefix="/fold")
# api_router.include_router(graph.router, tags=["graphs"], prefix="/graph")
# api_router.include_router(label.router, tags=["labels"], prefix="/label")
# api_router.include_router(labeling.router, tags=["labelings"], prefix="/labeling")
# api_router.include_router(labelingset.router, tags=["labelingSets"], prefix="/labelingset")
# api_router.include_router(nomenclature.router, tags=["nomenclatures"], prefix="/nomenclature")
# api_router.include_router(sharedlabelingset.router, tags=["sharedLabelingSets"], prefix="/sharedlabelingset")
api_router.include_router(species.router, tags=["species"], prefix="/species")
# api_router.include_router(subject.router, tags=["subjects"], prefix="/subject")