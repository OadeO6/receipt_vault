from typing import Annotated
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.connection import init_db
from app.receipt.service import ReceiptService
from app.user.models import User
from app.user.service import UserService
from app.utils.auth import verify_token
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.receipt.repo import ReceiptRepository
from app.schemas import FileType
from app.services.file_handler import FileHandlerService
from app.user.repo import UserRepository



reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/{settings.API_V1_STR}/user/login"
)

SessionDep = Annotated[Session, Depends(init_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
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

def get_user_service(
    user_repo: UserRepo
):
    return UserService(user_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    token: TokenDep,
    user_service: UserServiceDep
) -> User:
    try:
        user_data = verify_token(token)
        if not user_data:
            raise HTTPException(status_code=403, detail="Invalid token")
        _user = await user_service.get_user_by_email(user_data.email)
        if not _user:
            raise HTTPException(status_code=403, detail="Invalid token")
        return _user
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid token")


CurrentUser = Annotated[User, Depends(get_current_user)]
