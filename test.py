import requests
import xml.etree.ElementTree as ET

# 虎扑 NBA 新闻 RSS 地址
rss_url = "https://voice.hupu.com/nba/rss.xml"

# 发送 GET 请求获取 RSS 数据
response = requests.get(rss_url)
print(response)
response.raise_for_status()  # 如果请求失败，抛出异常

# 解析 XML 数据
root = ET.fromstring(response.content)

# 提取新闻条目
news_items = []
for item in root.findall(".//item"):
    title = item.find("title").text
    link = item.find("link").text
    pub_date = item.find("pubDate").text
    description = item.find("description").text
    news_items.append({
        "title": title,
        "link": link,
        "pubDate": pub_date,
        "description": description
    })

# 打印前 5 条新闻
for news in news_items[:5]:
    print(f"标题: {news['title']}")
    print(f"链接: {news['link']}")
    print(f"发布时间: {news['pubDate']}")
    print(f"描述: {news['description']}")
    print("-" * 80)
