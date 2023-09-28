from pydantic import BaseModel


class Product(BaseModel):
    name: str
    description: str
    price: float
    size: int
    temperature: str

    class Config:
        orm_mode = True
