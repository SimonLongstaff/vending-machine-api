from pydantic import BaseModel


class VendingItemLink(BaseModel):
    vending_machine_id: str
    product_id: str

    class Config:
        orm_mode = True
