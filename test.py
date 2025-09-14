import json
import requests

def geocode_amap(address, key):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": address,
        "key": key
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    key = "52208ef7a775c3eae0f1176ab1b684bc"
    address = "成都市武侯区银泰城"
    data = geocode_amap(address, key)

    print(data)

    location = data["geocodes"][0]["location"]
    lon, lat = map(float, location.split(","))  # 分别拿经度和纬度
    print("经度:", lon, "纬度:", lat)
    # 拼接到 Open-Meteo API
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather = requests.get(weather_url).json()
    print("天气:", weather)
