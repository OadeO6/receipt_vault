from sqlalchemy import create_engine
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DB_URL = str(settings.SQLALCHEMY_DATABASE_URI)

# async def init_async_db():
#     engine = create_async_engine(DB_URL)
#     AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
#     async with AsyncSessionLocal() as session:
#         yield session

sync_engine = create_engine(DB_URL, echo=True)
def init_db():
    SessionLocal = sessionmaker(bind=sync_engine)
    with SessionLocal() as session:
        yield session
