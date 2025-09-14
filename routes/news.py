from fastapi import APIRouter, HTTPException
from service.news import get_news

router = APIRouter()
@router.get("/{platform}")
async def get_latest_news(platform: str,limit:int=10):
    return await get_news(platform=platform,limit=limit)