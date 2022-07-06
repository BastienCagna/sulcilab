from pydantic import BaseModel
from sulcilab.core.schemas import SulciLabReadingModel


class ColorBase(BaseModel):
    name: str
    red: int
    green: int
    blue: int
    alpha: int

class ColorCreate(ColorBase):
    pass

class Color(ColorBase, SulciLabReadingModel):
    id: int
