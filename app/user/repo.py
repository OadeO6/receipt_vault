from sqlalchemy.orm import Session
from app.user.models import User
from app.user.schemas import UserRegister


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: UserRegister):
        user = User(
            name=user.name,
            email=user.email,
            password=user.password
        )
        a = self.session.add(user)
        print(a)
        self.session.commit()
