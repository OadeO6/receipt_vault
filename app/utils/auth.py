from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
import jwt

from app.core.config import settings
from app.core.logger import CustomLogger
from app.user.schemas import AccessTokenRes, AccessTokenSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = CustomLogger(__name__)


def generate_token(data: AccessTokenSchema, expiration_min: int | None = None, expires: bool = False) -> AccessTokenRes:
    expires_in = None
    if expires:
        if expiration_min:
            expiration_min = expiration_min
        else:
            expiration_min = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        expires_in = datetime.now(timezone.utc) + timedelta(seconds=expiration_min * 60)
    obj = {"sub": data.model_dump_json()}
    if expires_in:
        obj["exp"] = expires_in.isoformat()
    token = jwt.encode(obj, 'settings.SECRET_KEY', algorithm=settings.TOKEN_ALGORITHM)

    return AccessTokenRes(access_token=token, expires_in_minutes=expires_in)


def verify_token(token: str) -> AccessTokenSchema | None:
    if not token:
        return None
    if token.lower().startswith("bearer "):
        token = token.split(" ")[1]
    try:
        data = jwt.decode(token, 'settings.SECRET_KEY', algorithms=[settings.TOKEN_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        return None
    except Exception as e:
        logger.warning(f"Unexpected Error occurred while verifying token: {e}")
        return None
    # check if it has expired
    if "exp" in data and datetime.now(timezone.utc) > datetime.fromisoformat(data["exp"]):
        return None
    try:
        user = AccessTokenSchema.model_validate(eval(data["sub"]))
    except Exception:
        return None
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception as e:
        logger.warning(f"Unexpected Error occurred while verifying password: {e}")
    return False


def generate_password_hash(password: str) -> str:
    return pwd_context.hash(password)
