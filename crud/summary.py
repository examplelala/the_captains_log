from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, select
from datetime import datetime, date, timezone
from typing import List, Optional
import json
from models.daily_record import DailyRecord
from models.ai_data import AISummary
from service.llm import ai_service
from datetime import timedelta
class AISummaryCRUD:


    async def generate_ai_summary_task(db: AsyncSession, user_id: int, daily_record_id: int):
        """生成AI总结的后台任务"""
        try:
            # 获取记录数据
            # 修改查询方式为异步
            result = await db.execute(select(DailyRecord).filter(DailyRecord.id == daily_record_id))
            record = result.scalars().first()

            if not record:
                return
            current_date_str = record.record_date
            current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
            
            # 计算3天前的日期
            start_date = current_date - timedelta(days=3)
            start_date_str = start_date.strftime('%Y-%m-%d')
            
            # 查询历史记录（字符串比较）
            result = await db.execute(
                select(DailyRecord)
                .filter(
                    DailyRecord.user_id == user_id,
                    DailyRecord.record_date >= start_date_str,  # 字符串比较
                    DailyRecord.record_date <= current_date_str  # 字符串比较
                )
                .order_by(DailyRecord.record_date.asc())
            )
            historical_records = result.scalars().all()
            records_data = []
            for record in historical_records:
                record_data = {
                    "record_date": record.record_date,
                    "content": record.content,
                    "mood_score": record.mood_score,
                    "reflections": record.reflections,
                    "work_activities": json.loads(record.work_activities) if record.work_activities else [],
                    "personal_activities": json.loads(record.personal_activities) if record.personal_activities else [],
                    "learning_activities": json.loads(record.learning_activities) if record.learning_activities else [],
                    "health_activities": json.loads(record.health_activities) if record.health_activities else [],
                    "goals_achieved": json.loads(record.goals_achieved) if record.goals_achieved else [],
                    "challenges_faced": json.loads(record.challenges_faced) if record.challenges_faced else []
                }
                records_data.append(record_data)


            
            # 生成AI总结
            summary_data = await ai_service.generate_daily_summary_with_history(records_data)
            

            await AISummaryCRUD.create_ai_summary(db, user_id, daily_record_id, summary_data)
        
        except Exception as e:
            print(f"生成AI总结失败: {str(e)}")

    @staticmethod
    async def create_ai_summary(db: AsyncSession, user_id: int, daily_record_id: int, summary_data: dict) -> AISummary:
        result = await db.execute(select(DailyRecord).filter(DailyRecord.id == daily_record_id))
        record = result.scalars().first()
        if not record:
            raise ValueError("日记录不存在")
        
        # 检查是否已存在AI总结
        result = await db.execute(select(AISummary).filter(AISummary.daily_record_id == daily_record_id))
        existing_summary = result.scalars().first()

        if existing_summary:
            # 更新现有总结
            for field, value in summary_data.items():
                if hasattr(existing_summary, field):
                    if field in ['tomorrow_suggestions', 'priority_tasks', 'improvement_suggestions'] and isinstance(value, list):
                        setattr(existing_summary, field, json.dumps(value, ensure_ascii=False))
                    else:
                        setattr(existing_summary, field, value)
            
            existing_summary.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(existing_summary)
            return existing_summary
        
        db_summary = AISummary(
            user_id=user_id,
            daily_record_id=daily_record_id,
            **{k: v for k, v in summary_data.items() if k not in ['tomorrow_suggestions', 'priority_tasks', 'improvement_suggestions']}
        )
        
        # 处理列表字段
        if 'tomorrow_suggestions' in summary_data:
            db_summary.tomorrow_suggestions = json.dumps(summary_data['tomorrow_suggestions'], ensure_ascii=False)
        if 'priority_tasks' in summary_data:
            db_summary.priority_tasks = json.dumps(summary_data['priority_tasks'], ensure_ascii=False)
        if 'improvement_suggestions' in summary_data:
            db_summary.improvement_suggestions = json.dumps(summary_data['improvement_suggestions'], ensure_ascii=False)
        
        db.add(db_summary)
        await db.commit()
        await db.refresh(db_summary)
        return db_summary
    
    @staticmethod
    async def get_ai_summary(db: AsyncSession, user_id: int, summary_date: str) -> Optional[AISummary]:
        result = await db.execute(
            select(AISummary).filter(and_(AISummary.user_id == user_id, AISummary.summary_date == summary_date))
        )
        return result.scalars().first()
    
    @staticmethod
    async def get_user_summaries(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 30) -> List[AISummary]:
        result = await db.execute(
            select(AISummary).filter(AISummary.user_id == user_id)
            .order_by(desc(AISummary.summary_date)).offset(skip).limit(limit)
        )
        return result.scalars().all()