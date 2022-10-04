from pydantic import BaseModel

class SulciLabReadingModel(BaseModel):
    id: int
    # create_at: datetime
    # updated_at: datetime | None = None

    class Config:
        orm_mode = True
