from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, select
from datetime import datetime, date, timezone
from typing import List, Optional
import json
from schemas.record import DailyRecordCreate, DailyRecordUpdate
from models.daily_record import DailyRecord
from service.embedding import generate_vectors

class DailyRecordCRUD:
    @staticmethod
    async def create_daily_record(db: AsyncSession, user_id: int, record: DailyRecordCreate, record_date: str = None) -> DailyRecord:
        if not record_date:
            record_date = date.today().strftime('%Y-%m-%d')
        
        
        db_record = DailyRecord(
            user_id=user_id,
            record_date=record_date,
            content=record.content,
            mood_score=record.mood_score,
            reflections=record.reflections,
            vector=generate_vectors(record.content)
        )
        
        # 设置活动数据
        if record.work_activities:
            db_record.work_activities = json.dumps(record.work_activities, ensure_ascii=False)
        if record.personal_activities:
            db_record.personal_activities = json.dumps(record.personal_activities, ensure_ascii=False)
        if record.learning_activities:
            db_record.learning_activities = json.dumps(record.learning_activities, ensure_ascii=False)
        if record.health_activities:
            db_record.health_activities = json.dumps(record.health_activities, ensure_ascii=False)
        if record.goals_achieved:
            db_record.goals_achieved = json.dumps(record.goals_achieved, ensure_ascii=False)
        if record.challenges_faced:
            db_record.challenges_faced = json.dumps(record.challenges_faced, ensure_ascii=False)
        
        db.add(db_record)
        await db.commit()
        await db.refresh(db_record)
        return db_record
    
    @staticmethod
    async def get_daily_record(db: AsyncSession, user_id: int, record_date: str) -> Optional[DailyRecord]:
        result = await db.execute(
            select(DailyRecord).filter(
                and_(DailyRecord.user_id == user_id, DailyRecord.record_date == record_date)
            )
        )
        return result.scalars().first()
    
    @staticmethod
    async def get_user_records(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 30) -> List[DailyRecord]:
        result = await db.execute(
            select(DailyRecord).filter(DailyRecord.user_id == user_id)
            .order_by(desc(DailyRecord.record_date)).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_daily_record(db: AsyncSession, user_id: int, record_date: str, record_update: DailyRecordUpdate) -> Optional[DailyRecord]:
        result = await db.execute(
            select(DailyRecord).filter(
                and_(DailyRecord.user_id == user_id, DailyRecord.record_date == record_date)
            )
        )
        db_record = result.scalars().first()
        
        if not db_record:
            return None
        
        update_data = record_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['work_activities', 'personal_activities', 'learning_activities', 
                        'health_activities', 'goals_achieved', 'challenges_faced'] and value is not None:
                setattr(db_record, field, json.dumps(value, ensure_ascii=False))
            else:
                setattr(db_record, field, value)
        
        db_record.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_record)
        return db_record
    
    @staticmethod
    async def delete_daily_record(db: AsyncSession, user_id: int, record_date: str) -> bool:
        result = await db.execute(
            select(DailyRecord).filter(
                and_(DailyRecord.user_id == user_id, DailyRecord.record_date == record_date)
            )
        )
        db_record = result.scalars().first()
        
        if db_record:
            await db.delete(db_record)
            await db.commit()
            return True
        return False