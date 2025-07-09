import uuid
from sqlalchemy import UUID, Column, Computed, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.model import Base


class Receipt(Base):
    __tablename__ = "receipt"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)


    sub_total = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    discount = Column(Integer, nullable=False)
    tax = Column(Integer, nullable=False)
    currency = Column(String, nullable=False) # TODO: use enum

    payment_method = Column(String, nullable=False) # TODO: use enum
    issued_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cashier_name = Column(Integer, nullable=False)
    image_url = Column(String, nullable=False)
    category = Column(String, nullable=False) # TODO: Use enum

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Items(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipt.id"), nullable=False)
    description = Column(String, nullable=False) # TODO: use text instead of string

    count = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    total_price = Column(Integer, Computed("count * unit_price", persisted=True))


    receipt = relationship("Receipt", foreign_keys=["receipt_id"])
