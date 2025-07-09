import secrets
from typing import Any

from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_V1_STR: str
    # TODO: Fix env loading
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_USER: str = "user"
    POSTGRES_DB: str = "db"
    POSTGRES_PORT: int = 5433
    POSTGRES_SERVER: str
    PROJECT_NAME: str = "Receipt Vault"

    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        # Ensure all required components are present in the data
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        host = info.data.get("POSTGRES_SERVER")
        port = info.data.get("POSTGRES_PORT")
        db = info.data.get("POSTGRES_DB")

        if all([user, password, host, port, db]):
            return PostgresDsn.build(
                scheme="postgresql",
                username=user,
                password=password,
                host=host,
                port=port,
                path=f"{db}",
            )
        raise ValueError(f"{user}{password}{host}{port}{db}")


settings = Settings()
