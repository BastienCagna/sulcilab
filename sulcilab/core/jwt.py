from pydantic import BaseModel

class PJWT(BaseModel):
    token: str