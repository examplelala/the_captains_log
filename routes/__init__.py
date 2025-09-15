from fastapi import FastAPI
from routes.weather import router as weather_router
from routes.news import router as news_router
from routes.frontend import router as frontend_router
from routes.summary import router as summary_router
from routes.record import router as record_router
from routes.user import router as user_router
def register_routes(app: FastAPI):
    app.include_router(weather_router, prefix="/weather", tags=["Weather"])
    app.include_router(news_router, prefix="/news", tags=["News"])
    app.include_router(frontend_router, tags=["Frontend"])
    app.include_router(summary_router, prefix="/summary", tags=["Summary"])
    app.include_router(record_router, prefix="/record", tags=["Record"])
    app.include_router(user_router, prefix="/user", tags=["User"])