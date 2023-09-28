import datetime
import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.logger import logger
from fastapi_sqlalchemy import db

from models.schema import VendingItemLink as ModelVendingItemLink
from models.schema import VendingMachine as ModelVendingMachine
from models.vending_machine import VendingMachine

router = APIRouter(
    tags=["vending_machines"],
    prefix="/vending_machines"
)


@router.get(path="")
async def get_vending_machines():
    try:
        vending_machines = db.session.query(ModelVendingMachine).all()
        return vending_machines
    except Exception as e:
        logger.error(f"Error fetching vending machines: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(path="_local")
async def get_vending_machines_local(lat1: float, lng1: float, lat2: float, lng2: float):
    try:
        vending_machines = db.session.query(ModelVendingMachine).filter(
            ModelVendingMachine.lat.between(lat1, lat2),
            ModelVendingMachine.lng.between(lng1, lng2)
        ).all()
        return vending_machines
    except Exception as e:
        logger.error(f"Error fetching local vending machines: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(path="_search_product")
async def get_vending_machines_search_product(product_id: str):
    try:
        vending_machines = db.session.query(ModelVendingMachine).filter(
            ModelVendingMachine.products.any(id=product_id)
        ).all()
        return vending_machines
    except Exception as e:
        logger.error(f"Error searching vending machines by product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(path="/{vending_machine_id}")
async def get_vending_machine(vending_machine_id: str):
    try:
        vending_machine = db.session.query(ModelVendingMachine).filter(
            ModelVendingMachine.id == vending_machine_id).first()
        if vending_machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vending machine not found")
        return vending_machine
    except Exception as e:
        logger.error(f"Error fetching vending machine by ID: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(path="")
async def create_vending_machine(vending_machine: VendingMachine):
    try:
        new_vending_machine = ModelVendingMachine(
            name=vending_machine.name,
            lat=vending_machine.lat,
            lng=vending_machine.lng,
            hasBin=vending_machine.hasBin
        )
        db.session.add(new_vending_machine)
        db.session.commit()
        return {"message": "Vending machine created"}
    except Exception as e:
        logger.error(f"Error creating vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put(path="/{vending_machine_id}")
async def update_vending_machine(vending_machine_id: str, vending_machine: VendingMachine):
    try:
        db.session.query(ModelVendingMachine).filter(ModelVendingMachine.id == vending_machine_id).update({
            "name": vending_machine.name,
            "lat": vending_machine.lat,
            "lng": vending_machine.lng,
            "hasBin": vending_machine.hasBin,
            "updated_at": datetime.datetime.now()
        })
        db.session.commit()
        logger.info(f"Vending machine updated: {vending_machine_id}")
        return {"message": "Vending machine updated"}
    except Exception as e:
        logger.error(f"Error updating vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{vending_machine_id}")
async def delete_vending_machine(vending_machine_id: str):
    try:
        db.session.query(ModelVendingMachine).filter(ModelVendingMachine.id == vending_machine_id).delete()
        db.session.commit()
        logger.info(f"Vending machine deleted: {vending_machine_id}")
        return {"message": "Vending machine deleted"}
    except Exception as e:
        logger.error(f"Error deleting vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{vending_machine_id}/products")
async def add_product_to_vending_machine(vending_machine_id: str, product_id: str):
    nid = str(uuid.uuid4())
    update = datetime.datetime.now()
    try:
        db.session.add(ModelVendingItemLink(
            id=nid,
            vending_machine_id=vending_machine_id,
            product_id=product_id
        ))
        db.session.query(ModelVendingMachine).filter(ModelVendingMachine.id == vending_machine_id).update({
            "updated_at": update
        })
        db.session.commit()
        logger.info(f"Product added to vending machine: {vending_machine_id}")

        return {"message": "Product added to vending machine"}
    except Exception as e:
        logger.error(f"Error adding product to vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{vending_machine_id}/products/{product_id}")
async def remove_product_from_vending_machine(vending_machine_id: str, product_id: str):
    try:
        db.session.query(ModelVendingItemLink).filter(
            ModelVendingItemLink.vending_machine_id == vending_machine_id,
            ModelVendingItemLink.product_id == product_id
        ).delete()
        db.session.commit()
        logger.info(f"Product removed from vending machine: {vending_machine_id}")
        return {"message": "Product removed from vending machine"}
    except Exception as e:
        logger.error(f"Error removing product from vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
