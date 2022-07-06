import enum 
# from os import listdir, makedirs
# import os.path as op
# import shutil

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from sulcilab.database import SulciLabBase, Base
from sulcilab.brainvisa import models

class User(Base, SulciLabBase):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    labelingsets = relationship("LabelingSet", back_populates="author")
    sharedsets = relationship("SharedLabelingSet", back_populates="target")

    # def __str__(self):
    #     return self.username


class BackupTriggering(enum.Enum):
    SCHEDULED = "scheduled"
    SYSTEM = "system"
    USER = "user"

# class BackupManager(models.Manager):
#     def create(self, **obj_data):
#         # Force the datetime to be set to now
#         if obj_data['datetime']:
#             obj_data['datetime'] = None

#         # Call the super method which does the actual creation
#         backup = super().create(**obj_data) # Python 3 syntax!!

#         # Copy the sulcilab directory except the backup folder on the backup folder
#         sulcilab_path = ""
#         backup_path = op.join(sulcilab_path, "backups", backup.id)
#         makedirs(backup_path)
#         print("Creating backup in:", backup_path)
#         for item in listdir(sulcilab_path):
#             if item != "backups":
#                 shutil.copytree(op.join(sulcilab_path, item), backup_path)

#         return backup

# class Backup(Base):
#     path = models.CharField(max_length=400)
#     datetime = models.DateTimeField(auto_now_add=True, blank=True)
#     triggering = models.CharField(max_length=30, choices=list((v, v) for v in BackupTriggering))
#     comment = models.TextField(null=True, blank=True)