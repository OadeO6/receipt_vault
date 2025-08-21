from app.receipt.schema import ItemsDetailsDict, ItemsDetailsSchema
from fastapi import APIRouter, UploadFile,  HTTPException

from app.receipt.service import ReceiptService
from app.dep import ReceiptServiceDep


router = APIRouter()


@router.post("/image")
async def upload_file(
    file: UploadFile,
    receiptService: ReceiptServiceDep
):
    image_loc = receiptService.store_image_init(file)
    success = receiptService.process_image(image_loc)
    if not success:
        return HTTPException(
            status=500,
            details="Something went wrong"
        )
    return {"status": "successful"}

# ItemDetailsDict actually works here too 😅
# just Using ItemsDetailsSchema just in case
@router.get("/", response_model=list[ItemsDetailsSchema])
async def get_receipts(
    receiptService: ReceiptServiceDep,
    business_name: str | None = None,
    invoice_number: str | None = None,
    payment_method: str | None = None,
    cashier_fuzzy_search: str | None = None,
    item_fuzzy_search: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    return receiptService.get_receipts(
        business_name=business_name,
        invoice_number=invoice_number,
        payment_method=payment_method,
        cashier_fuzzy_search=cashier_fuzzy_search,
        item_fuzzy_search=item_fuzzy_search,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
