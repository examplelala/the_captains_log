from fastapi import FastAPI
from routes.weather import router as weather_router
def register_routes(app: FastAPI):
    app.include_router(weather_router, prefix="/weather", tags=["Weather"])