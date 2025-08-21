from typing import Annotated
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.connection import init_db
from app.receipt.service import ReceiptService
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.receipt.repo import ReceiptRepository
from app.schemas import FileType
from app.services.file_handler import FileHandlerService
from app.user.repo import UserRepository



reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/{settings.API_V1_STR}/login/access-token"
)

SessionDep = Annotated[Session, Depends(init_db)]
TokenDep = Annotated[str, Depends()]
def get_user_repo(
        session: SessionDep
):
    return UserRepository(session)

UserRepo = Annotated[UserRepository, Depends(get_user_repo)]

def get_receipt_repo(
        session: SessionDep
):
    return ReceiptRepository(session)

ReceiptRepo = Annotated[ReceiptRepository, Depends(get_receipt_repo)]

def file_handler():
        return FileHandlerService('/', [FileType.JPEG.value, FileType.PNG.value])
FileHandlerDep = Annotated[FileHandlerService, Depends(file_handler)]

def get_receipt_service(
    file_handler: FileHandlerDep,
    receipt_repo: ReceiptRepo
):
    return ReceiptService(file_handler, receipt_repo)


ReceiptServiceDep = Annotated[ReceiptService, Depends(get_receipt_service)]
