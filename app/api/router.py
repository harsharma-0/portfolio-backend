from fastapi import APIRouter
from app.api.routes import contact, feedback, health, playground, portfolio

api_router = APIRouter()
for route in (health.router, portfolio.router, contact.router, feedback.router, playground.router): api_router.include_router(route)
