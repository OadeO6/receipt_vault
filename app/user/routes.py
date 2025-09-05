from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.dep import UserServiceDep
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.user.schemas import AccessTokenRes, UserLogin, UserRegister, UserRes
from app.user.service import UserService


router = APIRouter()


@router.post("/register")
async def register(user: UserRegister, user_service: UserServiceDep) -> UserRes:
    res = await user_service.create_user(user)
    return res


@router.post("/login")
async def login(userpre: Annotated[OAuth2PasswordRequestForm, Depends()], user_service: UserServiceDep) -> AccessTokenRes:
    user = UserLogin(email=userpre.username, password=userpre.password)
    res = await user_service.authenticate_user(user)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return res

@router.post("/logini2")
async def login2(user: UserLogin, user_service: UserServiceDep) -> AccessTokenRes:
    res = await user_service.authenticate_user(user)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return res
