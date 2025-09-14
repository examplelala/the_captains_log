import requests
from config import settings


async def geocode_amap(address):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": address,
        "key": settings.weather_api_key
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data_json = resp.json()
    location = data_json["geocodes"][0]["location"]
    lon, lat = map(float, location.split(","))
    return lon, lat