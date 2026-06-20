from fastapi import APIRouter, status
from typing import List
import uuid
from ..models.product import ProductCreate, Product

router = APIRouter()

# In-memory store
products_db = []

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate):
    new_product = Product(
        id=uuid.uuid4(),
        name=product_in.name,
        description=product_in.description,
        price=product_in.price
    )
    products_db.append(new_product)
    return new_product

@router.get("/products", response_model=List[Product])
async def get_products():
    return products_db
