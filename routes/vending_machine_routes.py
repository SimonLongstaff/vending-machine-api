import datetime
import uuid

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.logger import logger
from pydantic import BaseModel

from database_utils import get_db

router = APIRouter()


class VendingMachine(BaseModel):
    name: str
    lat: float
    lng: float


@router.get("/vending_machines", tags=["vending_machines"])
async def get_vending_machines(db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''SELECT * FROM vending_machines''')
        vending_machines = [dict(zip([key[0] for key in cur.description], vending_machine)) for vending_machine in
                            await cur.fetchall()]
        return vending_machines
    except Exception as e:
        logger.error(f"Error fetching vending machines: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/vending_machines_local", tags=["vending_machines"])
async def get_vending_machines_local(lat1: float, lng1: float, lat2: float, lng2: float,
                                     db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''SELECT * FROM vending_machines WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?''',
                          (lat1, lat2, lng1, lng2))
        vending_machines = [dict(zip([key[0] for key in cur.description], vending_machine)) for vending_machine in
                            await cur.fetchall()]
        return vending_machines
    except Exception as e:
        logger.error(f"Error fetching local vending machines: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/vending_machines_seach_product", tags=["vending_machines"])
async def get_vending_machines_seach_product(product_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute(
            '''SELECT * FROM vending_machines WHERE id IN (SELECT vending_machine_id FROM vending_item_link WHERE product_id=?)''',
            (product_id,))
        vending_machines = [dict(zip([key[0] for key in cur.description], vending_machine)) for vending_machine in
                            await cur.fetchall()]
        return vending_machines
    except Exception as e:
        logger.error(f"Error searching vending machines by product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/vending_machines/{vending_machine_id}", tags=["vending_machines"])
async def get_vending_machine(vending_machine_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''SELECT * FROM vending_machines WHERE id=?''', (vending_machine_id,))
        vending_machine = await cur.fetchone()
        if vending_machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vending machine not found")
        return vending_machine
    except Exception as e:
        logger.error(f"Error fetching vending machine by ID: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/vending_machines", tags=["vending_machines"])
async def create_vending_machine(vending_machine: VendingMachine, db: aiosqlite.Connection = Depends(get_db)):
    try:
        nid = str(uuid.uuid4())
        now = datetime.datetime.now()
        cur = await db.cursor()
        await cur.execute(
            '''INSERT INTO vending_machines (id, name, lat, lng, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)''',
            (nid, vending_machine.name, vending_machine.lat, vending_machine.lng, now, now))
        await db.commit()
        return {"message": "Vending machine created"}
    except Exception as e:
        logger.error(f"Error creating vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/vending_machines/{vending_machine_id}", tags=["vending_machines"])
async def update_vending_machine(vending_machine_id: str, vending_machine: VendingMachine,
                                 db: aiosqlite.Connection = Depends(get_db)):
    try:
        vending_machine.updated_at = datetime.datetime.now()
        cur = await db.cursor()
        await cur.execute(
            '''UPDATE vending_machines SET name=?,  lat=?, lng=?, updated_at=? WHERE id=?''',
            (
                vending_machine.name, vending_machine.lat, vending_machine.lng, vending_machine.updated_at,
                vending_machine_id))
        await db.commit()
        return {"message": "Vending machine updated"}
    except Exception as e:
        logger.error(f"Error updating vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/vending_machines/{vending_machine_id}", tags=["vending_machines"])
async def delete_vending_machine(vending_machine_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute('''DELETE FROM vending_machines WHERE id=?''', (vending_machine_id,))
        await db.commit()
        return {"message": "Vending machine deleted"}
    except Exception as e:
        logger.error(f"Error deleting vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/vending_machines/{vending_machine_id}/products", tags=["vending_machines"])
async def get_vending_machine_products(vending_machine_id: str, db: aiosqlite.Connection = Depends(get_db)):
    try:
        cur = await db.cursor()
        await cur.execute(
            '''SELECT * FROM products WHERE id IN (SELECT product_id FROM vending_item_link WHERE vending_machine_id=?)''',
            (vending_machine_id,))
        products = [dict(zip([key[0] for key in cur.description], product)) for product in await cur.fetchall()]
        return products
    except Exception as e:
        logger.error(f"Error fetching vending machine products: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/vending_machines/{vending_machine_id}/products", tags=["vending_machines"])
async def add_product_to_vending_machine(vending_machine_id: str, product_id: str,
                                         db: aiosqlite.Connection = Depends(get_db)):
    try:
        nid = str(uuid.uuid4())
        update = datetime.datetime.now()
        cur = await db.cursor()
        await cur.execute('''INSERT INTO vending_item_link (id, vending_machine_id, product_id) VALUES (?, ?, ?)''',
                          (nid, vending_machine_id, product_id))
        await cur.execute('''UPDATE vending_machines SET updated_at=? WHERE id=?''', (update, vending_machine_id))
        await db.commit()
        return {"message": "Product added to vending machine"}
    except Exception as e:
        logger.error(f"Error adding product to vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/vending_machines/{vending_machine_id}/products/{product_id}", tags=["vending_machines"])
async def remove_product_from_vending_machine(vending_machine_id: str, product_id: str,
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
