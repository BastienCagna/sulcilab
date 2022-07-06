from pydantic import BaseModel

from sulcilab.core.schemas import SulciLabReadingModel, User, UserBase
from sulcilab.data.schemas import Color


class BrainVisaDBBase(BaseModel):
    name: str
    description: str | None
    path: str
class BrainVisaDBCreate(BrainVisaDBBase):
    pass
class BrainVisaDB(BrainVisaDBBase, SulciLabReadingModel):
    subjects: list['SubjectBase'] = []

    class Config:
        orm_mode = True


class SpeciesBase(BaseModel):
    fr_name: str
    en_name: str
class Species(SpeciesBase, SulciLabReadingModel):
    pass


class SubjectBase(BaseModel):
    database_id: int
    center: str
    name: str
    species: Species
class SubjectCreate(SubjectBase):
    pass
class Subject(SubjectBase, SulciLabReadingModel):
    database: BrainVisaDB


class FoldBase(BaseModel):
    graph_id: int
    vertex: int
class FoldCreate(FoldBase):
    pass
class Fold(FoldBase, SulciLabReadingModel):
    # graph: Graph
    pass


class GraphBase(BaseModel):
    subject_id: int
    acquisition: str
    analysis: str
    hemisphere: str
    version: str
    session: str | None
class GraphCreate(GraphBase):
    pass
class Graph(GraphBase, SulciLabReadingModel):
    subject: Subject
    folds: list[Fold]

class Nomenclature(BaseModel):
    name: str
    default: bool
    labels: list['Label']

class LabelBase(BaseModel):
    shortname: str
    fr_name: str
    en_name: str
    fr_description: str
    en_description: str
    parent_id: int | None
    color_id: int
    nomenclature_id: int
    left: bool
    right: bool
    link: str
class LabelCreate(LabelBase):
    pass
class Label(LabelBase, SulciLabReadingModel):
    parent: 'Label'
    color: Color
    nomenclature: Nomenclature


class LabelingBase(BaseModel):
    fold_id: int
    label_id: int
    labelingset_id: int
    rate: float | None
    comment: str | None
class LabelingCreate(LabelingBase):
    pass
class Labeling(LabelingBase, SulciLabReadingModel):
    iterations: int

class LabelingSetBase(BaseModel):
    author_id: int
    graph_id: int
    nomenclature_id: int
    labelings: list[Labeling] = []
    comment: str | None
class LabelingSetCreate(LabelingSetBase):
    pass
class LabelingSet(LabelingSetBase, SulciLabReadingModel):
    author: UserBase
    graph: Graph
    nomenclature: Nomenclature

class SharedLabelingSetBase(BaseModel):
    labelingset: LabelingSet
    target: User
    mode: int
class SharedLabelingSetCreate(SharedLabelingSetBase):
    pass
class SharedLabelingSet(SharedLabelingSetBase, SulciLabReadingModel):
    pass