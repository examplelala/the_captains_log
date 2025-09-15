from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, select
from datetime import datetime, date, timezone
from typing import List, Optional
import json
from models.user import User, UserSettings
from pydantic import BaseModel

# 定义一个临时的 UserCreate 模型，实际项目中应该从 schemas 或 models 导入
class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None

class UserCRUD:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        db_user = User(username=user.username, email=user.email)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        # 创建默认用户设置
        user_settings = UserSettings(user_id=db_user.id)
        db.add(user_settings)
        await db.commit()
        
        return db_user
    
    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()
    
    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()