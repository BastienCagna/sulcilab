from datetime import datetime
from pydantic import BaseModel
from typing import Union


class SulciLabReadingModel(BaseModel):
    id: int
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime, None] = None

    class Config:
        orm_mode = True
