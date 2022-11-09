from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Union
from pydantic import BaseModel
import os.path as op
import ujson
from sulcilab.brainvisa.fold import PFold, PFoldBase

from sulcilab.brainvisa.subject import PSubject, PSubjectBase, Subject
from sulcilab.utils.io import check_dir, read_arg, write_arg
from sulcilab.auth.auth_bearer import JWTBearer
from sulcilab.database import SulciLabBase, Base, get_db
from sulcilab.core import crud
from sulcilab.core.schemas import SulciLabReadingModel
from sulcilab.core.user import PUser, User, get_user_by_token, oauth2_scheme
from sulcilab.utils.misc import filt_keys, sqlalchemy_to_pydantic_instance
from time import time

DEFAULT_OUTPUT_DATABASE_PATH = op.join(op.split(__file__)[0], "..", "..", "working_database")

#############
# ORM Model #
#############
class LabelingSet(Base, SulciLabBase):
    __tablename__ = "labelingsets"

    author_id = Column(Integer, ForeignKey("users.id"))
    # author = relationship("User", back_populates="labelingsets", uselist=False)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    graph = relationship("Graph", uselist=False)
    nomenclature_id = Column(Integer, ForeignKey("nomenclatures.id"))
    nomenclature = relationship("Nomenclature", uselist=False)
    labelings = relationship("Labeling", back_populates="labelingset")

    # TODO: reset update date each time that a labeling is updated
    
    # nomenclature = models.ForeignKey(Nomenclature, on_delete=models.CASCADE, default=None, related_name="labelingsets")
    # creation_date = models.DateTimeField(null=True)
    # commit_date = models.DateTimeField(null=True, blank=True)
    # name = models.CharField(max_length=150, null=True, blank=True)
    comment = Column(Text, nullable=True)

    def to_aims_graph(self):
        out_f = self.get_graph_path()
        # TODO: verify the comparison of the dates
        if op.isfile(out_f) and op.getmtime(out_f) > self.updated_at:
            # File is up to date. Nothing to do.
            return

        # Load the original graph
        metadata, nodes, edges = read_arg(self.graph.get_path(), with_meshes=False)

        # Set the name of each vertex using labelings
        for labeling in self.labelings:
            v = labeling.fold.vertex
            for vertex in nodes:
                if vertex['index'] == v:
                    vertex['name'] = labeling.label.shortname
                    break            

        # Save the new graph
        write_arg(out_f, metadata, nodes, edges)

    def get_graph_path(self):    
        # TODO: use graph.get_path() instead
        out_dir = check_dir(op.join(
            DEFAULT_OUTPUT_DATABASE_PATH, "default", self.graph.subject.name, "t1mri", self.graph.acquisition, self.graph.analysis, 
            "folds", self.graph
            .version, "sulcilab"))
        return op.join(out_dir, "{}{}_uid-{}.arg".format(self.graph.hemisphere.value, self.graph.subject.name, self.id))
        

##################
# Pydantic Model #
##################
class PLabelingSetBase(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    comment: Union[str, None] = ""
class PLabelingSetCreate(PLabelingSetBase):
    pass
class PLabelingSetWithoutLabelings(PLabelingSetBase, SulciLabReadingModel):
    # author: 'PUserBase'
    graph: "PGraph"
    # nomenclature: "PNomenclature"
class PLabelingSet(PLabelingSetWithoutLabelings):
    labelings: List["PLabeling"] = []

class PLabelingSetShort(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    comment: Union[str, None] = ""

from sulcilab.core.user import PUserBase, get_user_by_token
from .nomenclature import PNomenclature
from .graph import PGraph
from .labeling import PLabeling, PLabelingBase
PLabelingSet.update_forward_refs()
PLabelingSetWithoutLabelings.update_forward_refs()

###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PLabelingSet])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all(db, LabelingSet, skip=skip, limit=limit)

# @router.get("/ofuser", dependencies=[Depends(JWTBearer())], response_model=List[PLabelingSetWithoutLabelings])
# def get_labelingsets_of_user(user_id: int, skip: int = 0, limit: int = 500, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     cuser = get_user_by_token(db, token)
#     user = crud.get(db, User, user_id)
#     if user.id != cuser.id and not cuser.is_admin:
#         raise HTTPException(status_code=403, detail="Only admin can list labelings set of an other user.")
#     sub = crud.get(db, Subject, sub_id)

#     gids = list(g.id for g in sub.graphs)
#     query = db.query(LabelingSet).filter(LabelingSet.graph_id.in_(gids)).offset(skip)
#     if limit:
#         query = query.limit(limit)
    
#     return sqlalchemy_to_pydantic_instance(query.all(), PLabelingSetWithoutLabelings)

@router.get("/usersubject", dependencies=[Depends(JWTBearer())], response_model=List[PLabelingSetWithoutLabelings])
def get_labelingsets_of_user_for_a_subject(user_id: int, sub_id: int, skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_user_by_token(db, token)
    user = crud.get(db, User, user_id)
    if user.id != cuser.id and not cuser.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can list labelings set of an other user.")
    sub = crud.get(db, Subject, sub_id)

    gids = list(g.id for g in sub.graphs)
    query = db.query(LabelingSet).filter(LabelingSet.graph_id.in_(gids)).offset(skip)
    if limit:
        query = query.limit(limit)
    
    return sqlalchemy_to_pydantic_instance(query.all(), PLabelingSetWithoutLabelings)


@router.get("/demo", response_model=PLabelingSetWithoutLabelings)
def get_demo_labelingset(db: Session = Depends(get_db)):
    lset = crud.get_one_by(db, LabelingSet)
    if not lset:
        raise HTTPException(404, "No labeling set in the database.")
    return sqlalchemy_to_pydantic_instance(lset, PLabelingSetWithoutLabelings)


@router.get("/data")
def get_labelingset_data(lset_id: int, db: Session = Depends(get_db)):
    # Use the first labeling set for demo
    lset = crud.get(db, LabelingSet, lset_id)
    
    # TODO: verify the access rights!

    # tic = time()
    mesh = lset.graph.load_mesh()
    fmeshes = lset.graph.load_folds_meshes()
    folds = sqlalchemy_to_pydantic_instance(lset.graph.folds, PFold)
    labelings = sqlalchemy_to_pydantic_instance(lset.labelings, PLabelingBase)
    subject = sqlalchemy_to_pydantic_instance(lset.graph.subject, PSubjectBase)
    nomenclature = sqlalchemy_to_pydantic_instance(lset.nomenclature, PNomenclature)
    # print("Loading and formatting took {}s".format(time() - tic))
    return Response(ujson.dumps({
        'subject': subject,
        'mesh': mesh, 
        'folds_meshes': fmeshes,
        'folds': folds,
        # TODO: split the mesh loading from labelings loading
        'labelings': labelings, 
        'nomenclature': nomenclature 
    }), media_type="application/json")


# FIXME: Following functions failed to generate API description 
# (probably due to bad matching between oupt and response_models or input pydantic models)

# @router.post("/new", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
# def new_labelingset(item:PLabelingSetCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     user: PUser = get_user_by_token(db, token)

#     if item.author_id != user.id and not user.is_admin:
#         raise HTTPException(status_code=403, detail="Only admin can create labeling set for an other user.")
#     if len(item.labelings) > 0:
#         raise HTTPException(status_code=403, detail="New labeling set is expected to be empty.")

#     return crud.create(db, LabelingSet,
#         author_id=item.author_id, 
#         graph_id=item.graph_id, 
#         nomenclature_id=item.nomenclature_id
#     )


# @router.post("/save", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
# def save_labelingset(item:PLabelingSet, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     user: PUser = get_user_by_token(db, token)

#     if item.author_id != user.id and not user.is_admin:
#         raise HTTPException(status_code=403, detail="Only admin can modify labeling set for an other user.")

#     return crud.update(db, LabelingSet,
#         id=item.id,
#         author_id=item.author_id, 
#         graph_id=item.graph_id, 
#         nomenclature_id=item.nomenclature_id#,
#         #labelings=item.labelings cause problems if empty list
#     )

# @router.delete("/del", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
# def delete_labelingset(item:PLabelingSetCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     user: PUser = get_user_by_token(db, token)
    
#     if item.author_id != user.id and not user.is_admin:
#         raise HTTPException(status_code=403, detail="Only admin can delete labeling set for an other user.")

#     item = crud.get(db, LabelingSet, item.id)
#     crud.delete(db, LabelingSet, item.id)
#     return item