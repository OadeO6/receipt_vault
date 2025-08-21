from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.receipt.models import Items, Receipt
from app.receipt.repo import ReceiptRepository
from app.receipt.schema import BusinessData, ItemsData, ItemsDetailsDict, ReceiptData
from app.services.file_handler import FileHandlerService


class ReceiptService:
    def __init__(self, file_handler: FileHandlerService, receipt_repo: ReceiptRepository):
        self.file_handler = file_handler
        self.receipt_repo = receipt_repo

    def store_image_init(self, file, tags=None) -> str:
        # store image
        location = self.file_handler.store_file(file)
        # store imageb address and data like tags in redis
        # store in redis
        return location


    def process_image(self, location) -> bool:
        image = self.file_handler.get_file(location)
        print(image)
        # procesing

        data = {
            "business": {
                "name": "Jendol",
                "tel_number": 9057712331,
            },
            "order_id": "4b2730f2-82b3-464e-b870-3635c6f5a00a",
            "sub_total": 5000,
            "total": 5000,
            "discount": 0,
            "tax": 0,
            "currency":  "NGN",  # TODO: use correct currency // maybe a currency enum
            "payment_method": "cash",
            "issued_time": datetime.now(timezone.utc),
            "cashier_name": "Ade Ade",
            "items": [
                {"description": "Super pack spageti", "count": 10, "unit_price": 500}
            ],
            "extra": {}
        }
        # Just to be sure what ever is generated meets the schema requirement
        business_data = BusinessData(
            name=data["business"]["name"],
            tel_number=data["business"]["tel_number"]
        )
        receipt_data = ReceiptData(
            **data,
        )
        items_data = [ItemsData(**idata) for idata in data["items"]]

        success = self.receipt_repo.create_receipt_with_items(
            business_data,
            receipt_data, items_data
        )
        if not success:
            return False

        return True

    def get_businesses(
        self, user_id: UUID, location: tuple[float, float] | None = None,
        address: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[BusinessData]:
        return []

    def get_cashiers(
        self, business_id: str, skip: int = 0, limit: int = 100
    ) -> list[str]:
        return []

    def get_receipts_by_item_description(
        self, item_description: str, skip: int = 0, limit: int = 100
    ) -> list[Receipt]:
        return []

    def get_receipts(
        self,
        business_name: str | None = None,
        invoice_number: str | None = None,
        payment_method: str | None = None,
        cashier_fuzzy_search: str | None = None,
        item_fuzzy_search: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ItemsDetailsDict]:
        result = self.receipt_repo.get_items_with_filters(
            business_name,
            invoice_number,
            payment_method,
            cashier_fuzzy_search,
            item_fuzzy_search,
            start_date,
            end_date,
            skip,
            limit,
        )
        return result
