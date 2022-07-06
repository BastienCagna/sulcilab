import enum
import os.path as op
import string

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, Float
from sqlalchemy.orm import relationship

from sulcilab.database import SulciLabBase, Base


class BrainVisaDB(Base, SulciLabBase):
    __tablename__ = "databases"

    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    path = Column(Text)
    subjects = relationship("Subject", back_populates="database")


class DefaultSpecies(Enum):
    BABOON = ('Baboon', 'Babouin'),
    CHIMPENZEE = ('Chimpanzee', 'Chimpanzé'),
    GORILLA = ('Gorilla', 'Gorille'),
    HUMAN = ('Human', 'Humain'),
    MARMOUSET = ('Marmouset', 'Marmouset'),
    MACAQUE = ('Macaque', 'Macaque'),
    PONGO = ('Orang outan', 'Orang outan')

class Species(Base, SulciLabBase):
    __tablename__ = "species"

    fr_name = Column(String, unique=True, index=True)
    en_name = Column(String, unique=True, index=True)


class GraphVersion(enum.Enum):
    V30 = "3.0"
    V31 = "3.1"
    V32 = "3.2"
    V33 = "3.3"

class Hemisphere(enum.Enum):
    left = "L"
    right = "R"

class Subject(Base, SulciLabBase):
    __tablename__ = "subjects"

    database_id = Column(Integer, ForeignKey("databases.id"))
    database = relationship("BrainVisaDB")
    center = Column(String)
    name = Column(String)
    graphs = relationship("Graph", back_populates="subject")
    species_id = Column(Integer, ForeignKey("species.id"))
    species = relationship("Species")

    def __str__(self):
        return "Subject#{}: {}".format(self.id, self.name)

class Graph(Base, SulciLabBase):
    __tablename__ = "graphs"

    subject = relationship("Subject", back_populates="graphs")
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    acquisition = Column(String)
    analysis = Column(String)
    hemisphere = Column(Enum(Hemisphere))
    version = Column(Enum(GraphVersion))
    session = Column(String, nullable=True)
    folds = relationship("Fold", back_populates="graph")

    def get_mesh_path(self, type="white"):
        # db = BVDatabase(self.subject.database.path)
        # return db.get_from_template(
        #     'morphologist_mesh',
        #     center=self.analysis.subject.center,
        #     subject=self.analysis.subject.name,
        #     acquisition=self.analysis.subject.acquisition,
        #     analysis=self.analysis.analysis,
        #     hemi=self.hemisphere,
        #     type=type
        # )[0]
        v_path = op.join(self.subject.database.path, self.subject.center, "t1mri", self.acquisition, self.analysis, "folds", self.version)
        if not self.session:
            return op.join(v_path, "{}{}.arg".format(self.hemisphere, self.subject.name))
        else:
            return op.join(v_path, self.session, "{}{}_{}.arg".format(self.hemisphere, self.subject.name, self.session))

class Fold(Base, SulciLabBase):
    __tablename__ = "folds"

    graph_id = Column(Integer, ForeignKey("graphs.id"))
    graph = relationship("Graph", back_populates="folds")
    vertex = Column(Integer)


class Nomenclature(Base, SulciLabBase):
    __tablename__ = "nomenclatures"

    name = Column(String)
    default = Column(Boolean, default=False) # replace this by a value in settings and provide the suited controller
    labels = relationship("Label", back_populates="nomenclature")

    def __str__(self) -> str:
        return "Nomenclature#{}: {}".format(self.id, self.name)


class Label(Base, SulciLabBase):
    __tablename__ = "labels"

    shortname = Column(String)
    fr_name = Column(String)
    en_name = Column(String)
    fr_description = Column(Text)
    en_description = Column(Text)
    parent_id = Column(Integer, ForeignKey("labels.id"))
    parent = relationship("Label") #, back_populates="children")
    color_id = Column(Integer, ForeignKey("colors.id"))
    color = relationship("Color")
    # parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    # color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    left = Column(Boolean, default=False)
    right = Column(Boolean, default=False)
    link = Column(Text)

    nomenclature_id = Column(Integer, ForeignKey("nomenclatures.id"))
    nomenclature = relationship("Nomenclature", back_populates="labels", uselist=False)
    #nomenclatures = models.ManyToManyField(Nomenclature(), related_name="labels")

    def __str__(self) -> str:
        return "Label{}: {}".format(self.id, self.shortname)


class LabelingSet(Base, SulciLabBase):
    __tablename__ = "labelingsets"

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="labelingsets", uselist=False)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    graph = relationship("Graph", uselist=False)
    nomenclature_id = Column(Integer, ForeignKey("nomenclatures.id"))
    nomenclature = relationship("Nomenclature", uselist=False)
    labelings = relationship("Labeling", back_populates="labelingset")
    
    # nomenclature = models.ForeignKey(Nomenclature, on_delete=models.CASCADE, default=None, related_name="labelingsets")
    # creation_date = models.DateTimeField(null=True)
    # commit_date = models.DateTimeField(null=True, blank=True)
    # name = models.CharField(max_length=150, null=True, blank=True)
    comment = Column(Text, nullable=True)

    def to_aims_graph(self):
        pass


class Labeling(Base, SulciLabBase):
    __tablename__ = "labelings"

    fold_id = Column(Integer, ForeignKey("folds.id"))
    fold = relationship("Fold", uselist=False) #, back_populates="")
    label_id = Column(Integer, ForeignKey("labels.id"))
    label = relationship("Label", uselist=False)
    labelingset_id = Column(Integer, ForeignKey("labelingsets.id"))
    labelingset = relationship("LabelingSet", back_populates="labelings", uselist=False)
    iterations = Column(Integer, default=0)
    rate = Column(Float, nullable=True)
    comment = Column(Text, nullable=True)

    def __str__(self):
        return 'Labeling#{}: {} {}'.format(self.id, self.fold.id, self.label.id)



class SharingMode(enum.Enum):
    READONLY = 0
    COMMENT = 1
    EDIT = 2

class SharedLabelingSet(Base, SulciLabBase):
    __tablename__ = "sharedlabelingsets"

    labelingset_id = Column(Integer, ForeignKey("labelingsets.id"))
    labelingset = relationship("LabelingSet", uselist=False)
    target_id = Column(Integer, ForeignKey("users.id"))
    target = relationship("User", back_populates="sharedsets", uselist=False)
    mode = Column(Enum(SharingMode))
