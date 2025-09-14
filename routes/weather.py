from fastapi import APIRouter, HTTPException
from service.weather import get_weather

router = APIRouter()
@router.get("/{address}")
async def get_current_weather(address: str):
    return await get_weather(address)