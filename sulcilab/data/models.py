# from enum import Enum
# from os import listdir, makedirs
# import os.path as op
# import shutil


from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from sulcilab.database import SulciLabBase, Base


DEFAULT_COLOR_NAME = "Unnamed"


class Color(Base, SulciLabBase):
    __tablename__ = "colors"

    name = Column(String, default=DEFAULT_COLOR_NAME, index=True)
    red = Column(Integer)
    green = Column(Integer)
    blue = Column(Integer)
    alpha = Column(Integer)

    def __str__(self):
        return 'Color#{} {}: {} {} {} {}'.format(
            self.id, self.name, self.red, self.green, self.blue, self.alpha)

    def to_hex(self, with_alpha=False):
        if with_alpha:
            return '#{:02x}{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue, self.alpha)
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)
