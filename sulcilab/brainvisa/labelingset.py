from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import Session, relationship
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Union
from pydantic import BaseModel
import os.path as op

from sulcilab.utils.io import check_dir, read_arg, write_arg
from sulcilab.auth.auth_bearer import JWTBearer
from sulcilab.database import SulciLabBase, Base, SessionLocal, get_db
from sulcilab.core import crud
from sulcilab.core.schemas import SulciLabReadingModel
from sulcilab.core.user import PUser, User, get_user_by_token, oauth2_scheme
from sulcilab.brainvisa import nomenclature


DEFAULT_OUTPUT_DATABASE_PATH = op.join(op.split(__file__)[0], "..", "..", "working_database")

#############
# ORM Model #
#############
class LabelingSet(Base, SulciLabBase):
    __tablename__ = "labelingsets"

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="labelingsets", uselist=False)
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
    labelings: List["PLabeling"] = []
    comment: Union[str, None] = ""
class PLabelingSetCreate(PLabelingSetBase):
    pass
class PLabelingSet(PLabelingSetBase, SulciLabReadingModel):
    author: 'PUserBase'
    graph: "PGraph"
    nomenclature: "PNomenclature"

class PLabelingSetShort(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    comment: Union[str, None] = ""

from sulcilab.core.user import PUserBase, get_user_by_token
from .nomenclature import PNomenclature
from .graph import PGraph
from .labeling import PLabeling
PLabelingSetBase.update_forward_refs()
PLabelingSet.update_forward_refs()
###################
# CRUD Operations #
###################


##########
# Routes #
##########
router = APIRouter()

@router.get("/all", response_model=List[PLabelingSet])
def read(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # user = get_current_user(db, token)
    return crud.get_all(db, LabelingSet, skip=skip, limit=limit)


@router.post("/new", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
def new_labelingset(item:PLabelingSetCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user: PUser = get_user_by_token(db, token)

    if item.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can create labeling set for an other user.")
    if len(item.labelings) > 0:
        raise HTTPException(status_code=403, detail="New labeling set is expected to be empty.")

    return crud.create(db, LabelingSet,
        author_id=item.author_id, 
        graph_id=item.graph_id, 
        nomenclature_id=item.nomenclature_id
    )


@router.post("/save", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
def save_labelingset(item:PLabelingSet, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user: PUser = get_user_by_token(db, token)

    if item.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can modify labeling set for an other user.")

    return crud.update(db, LabelingSet,
        id=item.id,
        author_id=item.author_id, 
        graph_id=item.graph_id, 
        nomenclature_id=item.nomenclature_id#,
        #labelings=item.labelings cause problems if empty list
    )



@router.delete("/del", dependencies=[Depends(JWTBearer())], response_model=PLabelingSet)
def delete_labelingset(item:PLabelingSetCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user: PUser = get_user_by_token(db, token)
    
    if item.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin can delete labeling set for an other user.")

    return crud.delete(db, LabelingSet, item.id)