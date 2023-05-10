from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int