from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base_repo import BaseRepository
from app.user.models import User
from app.user.schemas import UserRegister
from app.utils.auth import generate_password_hash


class UserRepository(BaseRepository):
    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, user: UserRegister):
        user = User(
            name=user.name,
            email=user.email,
            password=generate_password_hash(user.password)
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    async def get_user_by_email(self, email: str):
        qyery = (
            select(User)
            .where(User.email == email)
        )
        result = self.session.execute(qyery)
        user = result.scalars().first()
        return user
