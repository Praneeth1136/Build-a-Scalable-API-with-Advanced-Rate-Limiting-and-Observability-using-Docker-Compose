from pydantic import BaseModel, Field
import uuid

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class Product(ProductCreate):
    id: uuid.UUID
