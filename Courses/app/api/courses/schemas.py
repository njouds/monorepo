from pydantic import BaseModel


class coursesResponse(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True


class coursesRequest(BaseModel):
    name: str
