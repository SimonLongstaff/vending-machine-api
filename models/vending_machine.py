from pydantic import BaseModel


class VendingMachine(BaseModel):
    name: str
    lat: float
    lng: float
    hasBin: bool

    class Config:
        orm_mode = True
