from datetime import datetime
from warnings import warn
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


DEFAULT_OUTPUT_DATABASE_PATH = op.join(op.split(__file__)[0], "..", "..", "working_database")

#############
# ORM Model #
#############
class LabelingSet(Base, SulciLabBase):
    __tablename__ = "labelingsets"

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", uselist=False)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    graph = relationship("Graph", uselist=False)
    nomenclature_id = Column(Integer, ForeignKey("nomenclatures.id"))
    nomenclature = relationship("Nomenclature", uselist=False)
    labelings = relationship("Labeling", back_populates="labelingset")
    sharings = relationship("SharedLabelingSet", back_populates="labelingset")

    # TODO: reset update date each time that a labeling is updated
    
    # nomenclature = models.ForeignKey(Nomenclature, on_delete=models.CASCADE, default=None, related_name="labelingsets")
    # creation_date = models.DateTimeField(null=True)
    # commit_date = models.DateTimeField(null=True, blank=True)
    # name = models.CharField(max_length=150, null=True, blank=True)
    comment = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("labelingsets.id"))
    parent = relationship("LabelingSet", uselist=False) #, back_populates="children")

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
    id: int = -1
    created_at: Union[datetime, str, None] = None #""#Union[str, None] = None
    updated_at: Union[datetime, str, None] = None
    parent_id: Union[int, None] = None

    author_id: int
    graph_id: int
    nomenclature_id: int
    comment: Union[str, None] = ""
    sharings: List["PSharedLabelingSetWithoutLabelingSet"] = []

class PLabelingSetCreate(PLabelingSetBase):
    pass
class PLabelingSetWithoutLabelings(PLabelingSetBase, SulciLabReadingModel):
    # author: 'PUserBase'
    graph: "PGraph"
    author: "PUserBase"
    nomenclature: "PNomenclatureWithoutLabels"
class PLabelingSet(PLabelingSetBase):
    labelings: List["PLabeling"] = []
    parent: Union[PLabelingSetBase, None] = None

class PLabelingSetShort(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    comment: Union[str, None] = ""

from sulcilab.core.user import PUserBase, get_user_by_token
from .nomenclature import Nomenclature, PNomenclature, PNomenclatureWithoutLabels
from .graph import Graph, PGraph
from .labeling import Labeling, PLabeling, PLabelingBase
from .sharedlabelingset import SharedLabelingSet, PSharedLabelingSetWithoutLabelingSet
PLabelingSetBase.update_forward_refs()
PLabelingSetCreate.update_forward_refs()
PLabelingSetWithoutLabelings.update_forward_refs()
PLabelingSet.update_forward_refs()
PLabelingSetShort.update_forward_refs()
# PSharedLabelingSetWithoutLabelingSet.update_forward_refs()

# PLabelingSetWithoutLabelings.update_forward_refs()

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
    # FIXME: .in_ seems to not work
    #query = db.query(LabelingSet).filter(LabelingSet.graph_id.in_(gids)).offset(skip)
    all_lsets = crud.get_all(db, LabelingSet)
    lsets = []
    for lset in all_lsets:
        if lset.author_id == user_id:
            lsets.append(lset)
    sharings = crud.get_by(db, SharedLabelingSet, target_id=user_id)
    for sharing in sharings:
        lsets.append(sharing.labelingset)

    # if limit:
    #     query = query.limit(limit)
    
    # lsets = query.all()
    return sqlalchemy_to_pydantic_instance(lsets, PLabelingSetWithoutLabelings)


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

@router.post("/new", dependencies=[Depends(JWTBearer())], response_model=PLabelingSetBase)
def new(graph_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser: PUser = get_user_by_token(db, token)

    # Get the graph
    graph = crud.get(db, Graph, graph_id)
    if not graph:
        raise HTTPException(status_code=404)

    # Use default nomenclature
    nomenclature = crud.get_one_by(db, Nomenclature, default=True)
    if not nomenclature:
        nomenclature = crud.get_all(db, Nomenclature, limit=1)[0]
        if not nomenclature:
            raise HTTPException(status_code=404, message="No nomenclature")
        warn("No default nomenclature found. Using " + nomenclature.name)

    lset = crud.create(db, LabelingSet,
        author_id=cuser.id, 
        graph_id=graph.id, 
        nomenclature_id=nomenclature.id,
        sharings=[]
    )

    # Create labelings
    for fold in graph.folds:
        crud.create(db, Labeling, commitAndRefresh=False,
            fold_id=fold.id, 
            label_id=None, 
            labelingset_id=lset.id
        )
    db.commit()
    return sqlalchemy_to_pydantic_instance(lset, PLabelingSetBase)#lset

@router.post("/duplicate", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
def duplicate(lset_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser: PUser = get_user_by_token(db, token)
    lset = crud.get(db, LabelingSet, lset_id)

    if lset is None:
        raise HTTPException(status_code=404)

    # TODO: verify that cuser have access to lset

    # Duplicate labeling set
    new_lset = crud.create(db, LabelingSet,
        author_id=cuser.id, 
        graph_id=lset.graph_id, 
        nomenclature_id=lset.nomenclature_id,
        parent_id=lset.id
    )

    # Duplicate labelings
    new_labelings = []
    for lab in lset.labelings:
        db_item = crud.create(db , Labeling, commitAndRefresh=False,
            fold_id = lab.fold_id,
            label_id = lab.label_id,
            labelingset_id = new_lset.id,
            iterations = 0,
            rate = lab.rate,
            comment = lab.comment
        )
        db.add(db_item)
        new_labelings.append(db_item)
    db.commit()
    return sqlalchemy_to_pydantic_instance(new_lset, PLabelingSetWithoutLabelings)#new_lset#crud.get(db, LabelingSet, new_lset.id)


@router.post("/", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
def save_labelingset(item:PLabelingSet, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_user_by_token(db, token)
    # Get true item to verify authorship
    lset = crud.get(db, LabelingSet, item.id)

    if lset is None:
        raise HTTPException(status_code=404)
    if lset.author_id != item.author_id:
        raise HTTPException(status_code=403, detail="Cannot change author through this method.")
    if item.author_id != cuser.id and not cuser.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can modify labeling set for an other user.")

    return crud.update(db, LabelingSet,
        id=item.id,
        author_id=item.author_id, 
        graph_id=item.graph_id, 
        nomenclature_id=item.nomenclature_id#,
        #labelings=item.labelings cause problems if empty list
    )

@router.post("/update", dependencies=[Depends(JWTBearer())])
def save_labelings(lset_id: int, labelings: List[PLabelingBase], token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser = get_user_by_token(db, token)

    lset = crud.get(db, LabelingSet, lset_id)

    if lset is None:
        raise HTTPException(status_code=404)
    if lset.author_id != cuser.id and not cuser.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can modify labeling set for an other user.")

    # List the label of the nomenclature
    authorized_label_ids = list(label.id for label in lset.nomenclature.labels)

    # Check that all the labelings already belongs to the labelingset and that labels belong to the used nomenclature
    for lab in labelings:
        if lab.labelingset_id != lset.id or not lab.label_id in authorized_label_ids:
            raise HTTPException(status_code=422, detail="Wrong data has been send.")

    for lab in labelings:
        labeling = crud.get(db, Labeling, lab.id)
        crud.update(db, Labeling, id=lab.id, 
            label_id=lab.label_id, 
            iterations=labeling.iterations + (1 if labeling.label_id != lab.label_id else 0),
            rate=lab.rate,
            comment=lab.comment
        )
    return None

@router.delete("/del", dependencies=[Depends(JWTBearer())])
def delete_labelingset(lset_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cuser: PUser = get_user_by_token(db, token)
    
    lset = crud.get(db, LabelingSet, lset_id)

    if lset is None:
        raise HTTPException(status_code=404)
    if lset.author_id != cuser.id and not cuser.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can delete labeling set for an other user.")

    # TODO: replace parent_id by None for forked sets
    
    crud.delete(db, LabelingSet, lset.id)
    return None

