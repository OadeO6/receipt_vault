from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.user.models import User
from app.user.repo import UserRepository
from app.user.schemas import AccessTokenRes, AccessTokenSchema, UserLogin, UserRegister
from app.utils.auth import generate_token, verify_password


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    async def create_user(self, user_data: UserRegister) -> User | None:
        try:
            res = await self.repo.create_user(user_data)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="User already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating user: {e}")
        return res

    async def authenticate_user(self, user_details: UserLogin) -> AccessTokenRes | None:
        email = user_details.username
        password = user_details.password
        user = await self.repo.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        token_data = AccessTokenSchema(email=user.email, user_id=user.id)
        token = generate_token(token_data)
        return token

    async def get_user_by_email(self, email: str) -> User | None:
        try:
            user = await self.repo.get_user_by_email(email)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting user: {e}")
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
