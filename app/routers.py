from fastapi import APIRouter
from app.user.routes import router as user_route

api_routers = APIRouter()
api_routers.include_router(user_route, prefix="/user", tags=["User"])
