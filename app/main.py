from time import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
import logging

from app.receipt.models import Items, Receipt



from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.model import Base
from app.routers import api_routers
from app.core.config import settings
from app.core.connection import sync_engine


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "error": "Internal Server Error"
            # "detail": str(exc)
        },
    )

# TODO: replace this with migration
@app.on_event("startup")
def create_schema():
    Base.metadata.create_all(bind=sync_engine)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

@app.get("/")
async def root():
    return {"message": "Welcome to the Learning Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_routers, prefix=f"/{settings.API_V1_STR}")

