from typing import Annotated
from fastapi import APIRouter

from app.dep import SessionDep, UserRepo
from app.user.repo import UserRepository
from app.user.schemas import UserRegister


router = APIRouter()


@router.post("/register")
async def register(user: UserRegister, user_repo: UserRepo):
    res = await user_repo.create_user(user)
    return res
