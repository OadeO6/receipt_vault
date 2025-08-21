import uuid
from sqlalchemy import ARRAY, UUID, BigInteger, Column, Computed, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.model import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    tel_number = Column(BigInteger, nullable=False)

    # TODO: name them required
    address = Column(String, nullable=True)
    # location = Column(POINT, nullable=True)
    location = Column(ARRAY(Float), nullable=True)  # (lat, lon)

    # Unique constraint
    __table_args__ = (UniqueConstraint("name", "tel_number", name="uq_business_name_tel_number"),)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    # user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)

    invoice_number = Column(String, nullable=True)
    sub_total = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    discount = Column(Integer, nullable=False)
    tax = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)  # TODO: use enum

    payment_method = Column(String, nullable=True)  # TODO: use enum
    issued_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    cashier_name = Column(String, nullable=True)

    image_url = Column(String, nullable=False)

    # unique constraints
    __table_args__ = (UniqueConstraint("business_id", "invoice_number", name="uq_receipt_business_id_invoice_number"),)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Items(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)
    description = Column(String, nullable=False)

    category = Column(String, nullable=True)

    count = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    total_price = Column(Integer, Computed("count * unit_price", persisted=True))
