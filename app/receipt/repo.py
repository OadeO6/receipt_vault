from datetime import datetime, timezone
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.logger import CustomLogger
from app.receipt.models import Business, Items, Receipt
from app.receipt.schema import BusinessCreate, ItemsCreate, ItemsDetailsDict, ReceiptCreate


logger = CustomLogger(__name__)


class ReceiptRepository:
    def __init__(self, session: Session):
        self.session = session

    def _handle_commit(
        self, commit=True, flush=False,
        return_obj=True, obj=None
    ):
        """
        Helper function to handle commit or flush operations.

        obj: object to refresh
        return_obj: if true refresh and return obj else no refresh and return None
        flush: if true flush else no flush and return None if both commit and flush are false
        commit: if true commit else no commit and return None if both commit and flush are false
        """
        print("commit:2", commit, "flush:", flush, "return_obj:", return_obj, "obj:", obj)
        try:
            if commit:
                self.session.commit()
            else:
                if flush:
                    print("3flushing")
                    self.session.flush()
        except IntegrityError as e:
            print("rolling back", e)
            self.session.rollback()
            raise e
        print("committingi999")
        if not commit and not flush:
            return None
        print("committing")
        if return_obj:
            print("refreshing")
            self.session.refresh(obj)
            return obj

    def create_bussiness(
        self, bdata: BusinessCreate,
        commit=True, flush=True, refresh=True
    ):
        business = Business(
            name=bdata.name,
            tel_number=bdata.tel_number,
            # address=bdata.address,
            # location=bdata.location
        )

        self.session.add(business)
        return self._handle_commit(commit, flush, refresh, business)

    def get_business(self, name: str, address: str | None = None) -> Business | None:
        query = (
            select(Business)
            .where(Business.name == name)
        )
        if address:
            query = query.where(Business.address == address)
        return self.session.execute(query).scalars().first()

    def create_receipt(
        self,
        rdata: ReceiptCreate, business_id: UUID4,
        commit=True, refresh=True,
        flush=True
    ) -> Receipt | None:
        receipt = Receipt(
            **rdata.model_dump(),
            business_id=business_id,
            image_url=""
        )
        self.session.add(receipt)

        return self._handle_commit(commit, flush, refresh, receipt)

    def create_items(
        self, idata: list[ItemsCreate], receipt_id: UUID4, commit=True
    ) -> list[Items] | None:
        items = [
            Items(**item.model_dump(), receipt_id=receipt_id) for item in idata
        ]
        self.session.add_all(items)
        self._handle_commit(commit, flush=True, return_obj=False)
        for item in items:
            self.session.refresh(item)

        return items

    def create_receipt_with_items(
        self, bdata: BusinessCreate,
        rdata: ReceiptCreate, idata: list[ItemsCreate]
    ) -> bool:
        # TODO: handle error well
        try:
            business = self.get_business(bdata.name, bdata.address)
            print("business:", business)
            if not business:
                business = self.create_bussiness(bdata, commit=False)
            receipt = self.create_receipt(rdata, business.id, commit=False)
            print("receipt:", receipt)
            self.create_items(idata, receipt.id, commit=False)
            self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Receipt creation transaction failed: {e}")
            self.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error creating receipt: {e}")
            self.session.rollback()
            return False
        return True


    def update_receipt(self):
        pass

    def get_receipt(self, receipt_id: UUID4) -> Receipt | None:
        query = (
            select(Receipt)
            .where(Receipt.id == receipt_id)
        )
        return self.session.execute(query).scalars().first()

    def get_receipts(
        self, user_id: UUID4 | None = None, business_name: str | None = None,

        start_date: datetime | None = None, end_date: datetime = datetime.now(
            timezone.utc
        ),
        skip: int = 0, limit: int = 100
    ):
        pass

    def get_items_with_filters(
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
        detailed: bool = True,
    ) -> list[ItemsDetailsDict]:
        from sqlalchemy.dialects.postgresql import to_tsvector, plainto_tsquery
        from sqlalchemy import func


        query = (
            select(
                Items.id,
                Items.description,
                Items.unit_price.label("price"),
                Items.count.label("quantity"),
                Items.total_price,
                Receipt.created_at.label("date_time"),
                Receipt.id.label("receipt_id"),
                Business.name.label("business_name"),
            )
            .join(Receipt, Items.receipt_id == Receipt.id, isouter=True)
            .join(Business, Receipt.business_id == Business.id, isouter=True)
        )

        if invoice_number:
            query = query.where(Receipt.invoice_number == invoice_number)
        if payment_method:
            query = query.where(Receipt.payment_method == payment_method)


        if business_name:
            print("business_name:")
            query = query.where(
                func.to_tsvector('english', Business.name).op('@@')(
                    func.plainto_tsquery('english', business_name)
                )
                | (func.similarity(Business.name, business_name) > 0.3)
            )

        if cashier_fuzzy_search:
            print("cashier_fuzzy_search:")
            query = query.where(
                func.to_tsvector('english', Receipt.cashier_name).op('@@')(
                    func.plainto_tsquery('english', cashier_fuzzy_search)
                )
                | (func.similarity(Receipt.cashier_name, cashier_fuzzy_search) > 0.3)
            )

        if item_fuzzy_search:
            print("item_fuzzy_search:")
            query = query.where(
                func.to_tsvector('english', Items.description).op('@@')(
                    func.plainto_tsquery('english', item_fuzzy_search)
                )
                | (func.similarity(Items.description, item_fuzzy_search) > 0.3)
            )

        # if cashier_fuzzy_search:
        #     query = query.where(
        #         to_tsvector("english", Receipt.cashier_name).match(
        #             plainto_tsquery("english", cashier_fuzzy_search)
        #         )
        #             | (func.similarity(Receipt.cashier_name, cashier_fuzzy_search) > 0.3)
        #     )
        #
        # if item_fuzzy_search:
        #     query = query.where(
        #         to_tsvector("english", Items.description).match(
        #             plainto_tsquery("english", item_fuzzy_search)
        #         )
        #             | (func.similarity(Items.description, item_fuzzy_search) > 0.3)
        #     )

        if start_date:
            query = query.where(Receipt.created_at >= start_date)
        if end_date:
            query = query.where(Receipt.created_at <= end_date)

        query = query.offset(skip).limit(limit)
        result = self.session.execute(query).mappings().all()
        return result
