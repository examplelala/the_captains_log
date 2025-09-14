from fastapi import FastAPI
from routes.weather import router as weather_router
from routes.news import router as news_router
from routes.frontend import router as frontend_router
def register_routes(app: FastAPI):
    app.include_router(weather_router, prefix="/weather", tags=["Weather"])
    app.include_router(news_router, prefix="/news", tags=["News"])
    app.include_router(frontend_router, tags=["Frontend"])