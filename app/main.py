from contextlib import asynccontextmanager
from time import time
from asgi_correlation_id import CorrelationIdMiddleware
from dramatiq.middleware import CurrentMessage, Shutdown
from fastapi import FastAPI, HTTPException, Request
import requests
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import dramatiq
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.exceptions import CustomError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from logging.config import dictConfig
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.core.logger import log_config, CustomLogger
from app.core.broker import broker
from app.instrumentation import get_tracer, initialize_logs, initialize_metrics, initialize_tracer
from app.receipt.models import Items, Receipt
from app.tasks.actors import count_words, example


from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.model import Base
from app.routers import api_routers
from app.core.config import settings
from app.core.connection import sync_engine

# TODO: Make rate limiting only for prod
limiter = Limiter(key_func=get_remote_address)


logger = CustomLogger(__name__)

initialize_tracer()
initialize_metrics()
initialize_logs()

tracer = get_tracer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup: Starting scheduler...")
    # TODO: replace this with migration
    # create_schema
    Base.metadata.create_all(bind=sync_engine)
    logger.info("App startup complete.")
    yield
    logger.info("App shutdown: Shutting down scheduler...")
    broker.close()
    logger.info("App shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


if settings.OBSERVABILITY:
    FastAPIInstrumentor.instrument_app(app, tracer_provider=initialize_tracer())

# configure logging
dictConfig(log_config)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(_: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "error": "Internal Server Error"
            # "detail": str(exc)
        },
    )

@app.exception_handler(CustomError)
async def custom_global_exception_handler(_: Request, exc: CustomError):
    error =  exc.name if exc.name else "Internal Server Error"
    exc.logger.error(f"Custon exception {error}", exc_info=exc)  if exc.logger else None

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": exc.code if exc.code else 500,
            "error": exc.message
            # "detail": str(exc)
        },
    )



class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(TimingMiddleware)




@app.get("/")
async def root():
    i = count_words.send("http://example.com")
    job_id = i.message_id
    logger.info(f"Enqueued baground Job: {job_id}")
    example.send()
    return {"message": "Welcome to the Learning Platform API"}
    # with tracer.start_as_current_span("root"):
    #     i = count_words.send("http://example.com")
    #     job_id = i.message_id
    #     logger.info(f"Enqueued baground Job: {job_id}")
    #     example.send()
    #     return {"message": "Welcome to the Learning Platform API"}

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
