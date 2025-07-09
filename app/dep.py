from typing import Annotated
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.connection import init_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.receipt.repo import ReceiptRepository
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
