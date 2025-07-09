import uuid
from sqlalchemy.orm import as_declarative, declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import UUID, Column, DateTime, func


Base = declarative_base()
# @as_declarative()
# class Base(DeclarativeBase):
#     # Optional auto table naming (from class name)
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()
#
#     # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
