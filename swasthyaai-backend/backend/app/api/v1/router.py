from fastapi import APIRouter

from app.api.v1 import auth, dashboard, district, health, inventory, janmitra, voice

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(inventory.router)
api_router.include_router(janmitra.router)
api_router.include_router(district.router)
api_router.include_router(voice.router)
