import datetime
import sqlite3
import uuid

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class VendingMachine(BaseModel):
    name: str
    lat: float
    lng: float


@router.get("/vending_machines", tags=["vending_machines"])
async def get_vending_machines():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM vending_machines''')
    vending_machines = cur.fetchall()
    vending_machines = [dict(zip([key[0] for key in cur.description], vending_machine)) for vending_machine in
                        vending_machines]

    conn.close()
    return vending_machines


@router.get("/vending_machines_local", tags=["vending_machines"])
async def get_vending_machines_local(lat1: float, lng1: float, lat2: float, lng2: float):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM vending_machines WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?''',
                (lat1, lat2, lng1, lng2))
    vending_machines = cur.fetchall()
    vending_machines = [dict(zip([key[0] for key in cur.description], vending_machine)) for vending_machine in
                        vending_machines]

    conn.close()
    return vending_machines


@router.get("/vending_machines_seach_product", tags=["vending_machines"])
async def get_vending_machines_seach_product(product_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(
        '''SELECT * FROM vending_machines WHERE id IN (SELECT vending_machine_id FROM vending_item_link WHERE product_id=?)''',
        (product_id,))
    vending_machines = cur.fetchall()
    vending_machines = [dict(zip([key[0] for key in cur.description], vending_machine)) for vending_machine in
                        vending_machines]

    conn.close()
    return vending_machines


@router.get("/vending_machines/{vending_machine_id}", tags=["vending_machines"])
async def get_vending_machine(vending_machine_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM vending_machines WHERE id=?''', (vending_machine_id,))
    vending_machine = cur.fetchone()
    conn.close()
    return vending_machine


@router.post("/vending_machines", tags=["vending_machines"])
async def create_vending_machine(vending_machine: VendingMachine):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    nid = uuid.uuid4()
    nid = str(nid)
    now = datetime.datetime.now()
    cur.execute(
        '''INSERT INTO vending_machines (id, name, lat, lng, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)''',
        (nid, vending_machine.name, vending_machine.lat, vending_machine.lng, now, now))
    conn.commit()
    conn.close()
    return {"message": "Vending machine created"}


@router.put("/vending_machines/{vending_machine_id}", tags=["vending_machines"])
async def update_vending_machine(vending_machine_id: str, vending_machine: VendingMachine):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    vending_machine.updated_at = datetime.datetime.now()
    cur.execute(
        '''UPDATE vending_machines SET name=?,  lat=?, lng=?, updated_at=? WHERE id=?''',
        (
            vending_machine.name, vending_machine.lat, vending_machine.lng, vending_machine.updated_at,
            vending_machine_id))
    conn.commit()
    conn.close()
    return {"message": "Vending machine updated"}


@router.delete("/vending_machines/{vending_machine_id}", tags=["vending_machines"])
async def delete_vending_machine(vending_machine_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''DELETE FROM vending_machines WHERE id=?''', (vending_machine_id,))
    conn.commit()
    conn.close()
    return {"message": "Vending machine deleted"}


@router.get("/vending_machines/{vending_machine_id}/products", tags=["vending_machines"])
async def get_vending_machine_products(vending_machine_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute(
        '''SELECT * FROM products WHERE id IN (SELECT product_id FROM vending_item_link WHERE vending_machine_id=?)''',
        (vending_machine_id,))
    products = cur.fetchall()
    products = [dict(zip([key[0] for key in cur.description], product)) for product in products]
    conn.close()
    return products


@router.post("/vending_machines/{vending_machine_id}/products", tags=["vending_machines"])
async def add_product_to_vending_machine(vending_machine_id: str, product_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    nid = uuid.uuid4()
    nid = str(nid)
    update = datetime.datetime.now()
    cur.execute('''INSERT INTO vending_item_link (id, vending_machine_id, product_id) VALUES (?, ?, ?)''',
                (nid, vending_machine_id, product_id))
    cur.execute('''UPDATE vending_machines SET updated_at=? WHERE id=?''', (update, vending_machine_id))
    conn.commit()
    conn.close()
    return {"message": "Product added to vending machine"}


@router.delete("/vending_machines/{vending_machine_id}/products/{product_id}", tags=["vending_machines"])
async def remove_product_from_vending_machine(vending_machine_id: str, product_id: str):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''DELETE FROM vending_item_link WHERE vending_machine_id=? AND product_id=?''',
                (vending_machine_id, product_id))
    conn.commit()
    conn.close()
    return {"message": "Product removed from vending machine"}
