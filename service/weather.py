import requests
from service.location import geocode_amap
async def get_weather_by_address(address):
    lon, lat = await geocode_amap(address)
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather = requests.get(weather_url).json()
    return weather
async def get_weather_by_coords(lon, lat):
    
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather = requests.get(weather_url).json()
    return weather
if __name__ == "__main__":
    pass