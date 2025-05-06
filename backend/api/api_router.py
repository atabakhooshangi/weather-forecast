from fastapi import APIRouter
from .endpoints import  forecast_router

api_router = APIRouter()

api_router.include_router(forecast_router, prefix="/forecast", tags=["forecast"])