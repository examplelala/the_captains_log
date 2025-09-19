from fastapi import APIRouter, HTTPException
from service.weather import get_weather_by_coords, get_weather_by_address

router = APIRouter()
@router.get("/{address}")
async def get_current_weather(address: str):
    return await get_weather_by_address(address)
@router.get("/{lon}/{lat}")
async def get_current_weather(lon: float, lat: float):
    return await get_weather_by_coords(lon, lat)