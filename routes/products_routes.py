import sqlite3
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Product(BaseModel):
    name: str
    description: str
    price: float
    size: int
    temperature: str


@router.get("/products", tags=["products"])
async def get_products():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM products''')
    products = cur.fetchall()
    products = [dict(zip([key[0] for key in cur.description], product)) for product in products]

    conn.close()
    return products


@router.get("/products_search", tags=["products"])
async def get_products_search(search: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM products WHERE name LIKE ?''', ('%' + search + '%',))
    products = cur.fetchall()
    products = [dict(zip([key[0] for key in cur.description], product)) for product in products]

    conn.close()
    return products


@router.get("/products/{product_id}", tags=["products"])
async def get_product(product_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM products WHERE id=?''', (product_id,))
    product = cur.fetchone()
    conn.close()
    return product


@router.post("/products", tags=["products"])
async def create_product(product: Product):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    nid = uuid.uuid4()
    nid = str(nid)
    cur.execute(
        '''INSERT INTO products (id, name, description, price, temperature) VALUES (?, ?, ?, ?, ?)''',
        (nid, product.name, product.description, product.price, product.temperature))
    conn.commit()
    conn.close()
    return {"message": "Product created"}


@router.put("/products/{product_id}", tags=["products"])
async def update_product(product_id: str, product: Product):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(
        '''UPDATE products SET name=?, description=?, price=?, temperature=? WHERE id=?''',
        (product.name, product.description, product.price, product.temperature, product_id))
    conn.commit()
    conn.close()
    return {"message": "Product updated"}


@router.delete("/products/{product_id}", tags=["products"])
async def delete_product(product_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''DELETE FROM products WHERE id=?''', (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted"}


@router.get("/products/{product_id}/vending_machines", tags=["products"])
async def get_product_vending_machines(product_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(
        '''SELECT * FROM vending_machines WHERE id IN (SELECT vending_machine_id FROM vending_item_link WHERE product_id=?)''',
        (product_id,))
    vending_machines = cur.fetchall()
    conn.close()
    return vending_machines


@router.post("/products/{product_id}/vending_machines", tags=["products"])
async def add_product_to_vending_machine(product_id: str, vending_machine_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''INSERT INTO vending_item_link (vending_machine_id, product_id) VALUES (?, ?)''',
                (vending_machine_id, product_id))
    conn.commit()
    conn.close()
    return {"message": "Product added to vending machine"}


@router.delete("/products/{product_id}/vending_machines/{vending_machine_id}", tags=["products"])
async def remove_product_from_vending_machine(product_id: str, vending_machine_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''DELETE FROM vending_item_link WHERE vending_machine_id=? AND product_id=?''',
                (vending_machine_id, product_id))
    conn.commit()
    conn.close()
    return {"message": "Product removed from vending machine"}
