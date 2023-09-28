import uuid

from sqlalchemy import Column, DateTime, String, Float, Boolean, UUID, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class VendingMachine(Base):
    __tablename__ = 'vending_machines'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    hasBin = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    products = relationship("VendingItemLink", back_populates="_vending_machine")


class Product(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    size = Column(Integer)
    temperature = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    vending_machines = relationship("VendingItemLink", back_populates="_product")


class VendingItemLink(Base):
    __tablename__ = 'vending_item_link'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vending_machine_id = Column(UUID(as_uuid=True), ForeignKey('vending_machines.id'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    _vending_machine = relationship("VendingMachine", back_populates="products")
    _product = relationship("Product", back_populates="vending_machines")
