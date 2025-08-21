from fastapi import APIRouter
from app.user.routes import router as user_route
from app.receipt.routes import router as receipt_route

api_routers = APIRouter()
api_routers.include_router(user_route, prefix="/user", tags=["User"])
api_routers.include_router(receipt_route, prefix="/receipt", tags=["Receipt"])
