from agents.langgraph.graph import respond
from models.user import User
from models.ai_data import AISummary
from database import get_async_session  
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

async def test():
    async for session in get_async_session():
        result = await respond(1, "最近让我开心的事情都有哪些", session)
        print(result)
        break  # 只取第一个（也是唯一的）session

if __name__ == "__main__":
    asyncio.run(test())