from datetime import datetime
from re import I
from typing import Annotated, TypedDict, get_type_hints
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field
from fastapi import File, UploadFile



def convert_typedict_to_pydantic_model(
    new_model_name: str, typed_dict_class: type
) -> type[BaseModel]:
    annotations = get_type_hints(typed_dict_class)
    return type(new_model_name, (BaseModel,), {"__annotations__": annotations})

class ItemsData(BaseModel):
    description: str
    count: int
    unit_price: int

class ItemsCreate(ItemsData):
    pass


class ReceiptData(BaseModel):
    sub_total: int
    total: int
    discount: int
    tax: int
    currency: str = "NGN"

    invoice_number: str | None = None
    payment_method: str | None = None
    issued_time: datetime
    cashier_name: str | None = None


class ReceiptCreate(ReceiptData):
    pass

class BusinessData(BaseModel):
    name: str
    tel_number: int

    address: str | None = None
    location: tuple[float, float] | None = None

class BusinessCreate(BusinessData):
    pass

class ItemsDetailsDict(TypedDict):
    id: UUID4
    description: str
    quantity: int
    price: int
    total_price: int
    receipt_id: UUID4
    business_name: str
    date_time: datetime


ItemsDetailsSchemaCopy = convert_typedict_to_pydantic_model(
    "ItemsDetailsSchema", ItemsDetailsDict
)


class ItemsDetailsSchema(ItemsDetailsSchemaCopy):
    pass
