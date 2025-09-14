import random
import requests
import asyncio
async def get_news(platform:str=None,limit:int=3):
    platform_codes = [
    "baidu",
    "shaoshupai",
    "weibo",
    "zhihu",
    "36kr",
    "52pojie",
    "bilibili",
    "douban",
    "hupu",
    "tieba",
    "juejin",
    "douyin",
    "v2ex",
    "jinritoutiao",
    "stackoverflow",
    "github",
    "hackernews"
]   
    if platform is None or platform not in platform_codes:
        platform=random.choice(platform_codes)
    else:
        platform=platform
    url=f"https://orz.ai/api/v1/dailynews?platform={platform}"
    response = requests.get(url)
    print("platform:",platform,"response",response.json())
    return response.json()["data"][:limit]
if __name__ == "__main__":
    asyncio.run(get_news())