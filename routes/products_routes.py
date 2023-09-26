import uuid

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.logger import logger
from pydantic import BaseModel

from database_utils import get_db

router = APIRouter()


class Product(BaseModel):
    name: str
    description: str
    price: float
    size: int
    temperature: str


@router.get("/products", tags=["products"])
async def get_products(db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''SELECT * FROM products''')
        products = [dict(zip([key[0] for key in cur.description], product)) for product in await cur.fetchall()]
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/products_search", tags=["products"])
async def get_products_search(search: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''SELECT * FROM products WHERE name LIKE ?''', ('%' + search + '%',))
        products = [dict(zip([key[0] for key in cur.description], product)) for product in await cur.fetchall()]
        return products
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/products/{product_id}", tags=["products"])
async def get_product(product_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''SELECT * FROM products WHERE id=?''', (product_id,))
        product = await cur.fetchone()
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except Exception as e:
        logger.error(f"Error fetching product by ID: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/products", tags=["products"])
async def create_product(product: Product, db: aiosqlite.Connection = Depends(get_db)):
    try:
        nid = str(uuid.uuid4())
        cur = await db.cursor()
        await cur.execute(
            '''INSERT INTO products (id, name, description, price, temperature) VALUES (?, ?, ?, ?, ?)''',
            (nid, product.name, product.description, product.price, product.temperature))
        await db.commit()
        return {"message": "Product created"}
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/products/{product_id}", tags=["products"])
async def update_product(product_id: str, product: Product, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute(
            '''UPDATE products SET name=?, description=?, price=?, temperature=? WHERE id=?''',
            (product.name, product.description, product.price, product.temperature, product_id))
        await db.commit()
        return {"message": "Product updated"}
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/products/{product_id}", tags=["products"])
async def delete_product(product_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''DELETE FROM products WHERE id=?''', (product_id,))
        await db.commit()
        return {"message": "Product deleted"}
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/products/{product_id}/vending_machines", tags=["products"])
async def get_product_vending_machines(product_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute(
            '''SELECT * FROM vending_machines WHERE id IN (SELECT vending_machine_id FROM vending_item_link WHERE product_id=?)''',
            (product_id,))
        vending_machines = await cur.fetchall()
        return vending_machines
    except Exception as e:
        logger.error(f"Error fetching product vending machines: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/products/{product_id}/vending_machines", tags=["products"])
async def add_product_to_vending_machine(product_id: str, vending_machine_id: str,
                                         db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''INSERT INTO vending_item_link (vending_machine_id, product_id) VALUES (?, ?)''',
                          (vending_machine_id, product_id))
        await db.commit()
        return {"message": "Product added to vending machine"}
    except Exception as e:
        logger.error(f"Error adding product to vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/products/{product_id}/vending_machines/{vending_machine_id}", tags=["products"])
async def remove_product_from_vending_machine(product_id: str, vending_machine_id: str,
                                              db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''DELETE FROM vending_item_link WHERE vending_machine_id=? AND product_id=?''',
                          (vending_machine_id, product_id))
        await db.commit()
        return {"message": "Product removed from vending machine"}
    except Exception as e:
        logger.error(f"Error removing product from vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
