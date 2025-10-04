from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker 
from models._base import Base
from config import settings
from models.ai_data import AISummary,AIAnalysisLog
from models.daily_record import DailyRecord
from models.task_template import TaskTemplate
from models.user import User, UserSettings




DATABASE_URL = settings.postgres_url
async_engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
if __name__ == "__main__":
    print(Base.metadata.tables.keys())
