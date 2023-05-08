from pydantic import BaseModel

class book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int