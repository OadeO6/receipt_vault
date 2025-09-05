
import uuid
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRes(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr

class AccessTokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int | None = None


class AccessTokenSchema(BaseModel):
    email: EmailStr
    user_id: uuid.UUID
