from fastapi import APIRouter, HTTPException, status
from fastapi.logger import logger
from fastapi_sqlalchemy import db

from models.product import Product
from models.schema import Product as ModelProduct

router = APIRouter(
    tags=["products"],
    prefix="/products"
)


@router.get(path="")
async def get_products():
    try:
        products = db.session.query(ModelProduct).all()
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post(path="")
async def create_product(product: Product):
    try:
        new_product = ModelProduct(
            name=product.name,
            description=product.description,
            price=product.price,
            size=product.size,
            temperature=product.temperature
        )
        db.session.add(new_product)
        db.session.commit()
        return {"message": "Product created"}
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(path="_search")
async def get_products_search(search: str):
    try:
        products = db.session.query(ModelProduct).filter(ModelProduct.name.like(f"%{search}%")).all()
        return products
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(path="/{product_id}")
async def get_product(product_id: str):
    try:
        product = db.session.query(ModelProduct).filter(ModelProduct.id == product_id).first()
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except Exception as e:
        logger.error(f"Error fetching product by ID: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put(path="/{product_id}")
async def update_product(product_id: str, product: Product):
    try:
        db.session.query(ModelProduct).filter(ModelProduct.id == product_id).update({
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "size": product.size,
            "temperature": product.temperature
        })
        db.session.commit()
        return {"message": "Product updated"}
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete(path="/{product_id}")
async def delete_product(product_id: str):
    try:
        db.session.query(ModelProduct).filter(ModelProduct.id == product_id).delete()
        db.session.commit()
        return {"message": "Product deleted"}
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get(path="/vending_machine/{vending_machine_id}")
async def get_products_by_vending_machine(vending_machine_id: str):
    try:
        products = db.session.query(ModelProduct).filter(
            ModelProduct.vending_machines.any(vending_machine_id=vending_machine_id)
        ).all()
        return products
    except Exception as e:
        logger.error(f"Error fetching products by vending machine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
# @router.get("/{product_id}/vending_machines")
# async def get_product_vending_machines(product_id: str, db: aiosqlite.Connection = Depends(get_db)):
#     try:
#         cur = await db.cursor()
#         await cur.execute(
#             '''SELECT * FROM vending_machines WHERE id IN (SELECT vending_machine_id FROM vending_item_link WHERE product_id=?)''',
#             (product_id,))
#         vending_machines = await cur.fetchall()
#         return vending_machines
#     except Exception as e:
#         logger.error(f"Error fetching product vending machines: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
#
#
# @router.post("/{product_id}/vending_machines")
# async def add_product_to_vending_machine(product_id: str, vending_machine_id: str,
#                                          db: aiosqlite.Connection = Depends(get_db)):
#     try:
#         cur = await db.cursor()
#         await cur.execute('''INSERT INTO vending_item_link (vending_machine_id, product_id) VALUES (?, ?)''',
#                           (vending_machine_id, product_id))
#         await db.commit()
#         return {"message": "Product added to vending machine"}
#     except Exception as e:
#         logger.error(f"Error adding product to vending machine: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
#
#
# @router.delete("/{product_id}/vending_machines/{vending_machine_id}")
# async def remove_product_from_vending_machine(product_id: str, vending_machine_id: str,
#                                               db: aiosqlite.Connection = Depends(get_db)):
#     try:
#         cur = await db.cursor()
#         await cur.execute('''DELETE FROM vending_item_link WHERE vending_machine_id=? AND product_id=?''',
#                           (vending_machine_id, product_id))
#         await db.commit()
#         return {"message": "Product removed from vending machine"}
#     except Exception as e:
#         logger.error(f"Error removing product from vending machine: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
