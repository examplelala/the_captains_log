# routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import json
from schemas.record import DailyRecordCreate,DailyRecordUpdate
from database import get_async_session
from crud.summary import AISummaryCRUD
from crud.record import DailyRecordCRUD
from crud.user import UserCRUD
from service.llm import ai_service
router = APIRouter()
@router.post("/users/{user_id}/records/", response_model=dict)
async def create_daily_record(
    user_id: int, 
    record: DailyRecordCreate, 
    background_tasks: BackgroundTasks,
    record_date: Optional[str] = None,
    db: Session = Depends(get_async_session)
):
    """创建每日记录"""
    try:
        # 验证用户存在
        user = await UserCRUD.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        analyzed_record = await ai_service.analyze_daily_content(record.content)
        # 创建记录
        db_record = await DailyRecordCRUD.create_daily_record(db, user_id, analyzed_record, record_date)
        
        # 异步生成AI总结
        background_tasks.add_task(AISummaryCRUD.generate_ai_summary_task, db, user_id, db_record.id)
        
        return {
            "id": db_record.id,
            "user_id": db_record.user_id,
            "record_date": db_record.record_date,
            "content": db_record.content,
            "mood_score": db_record.mood_score,
            "created_at": db_record.created_at,
            "message": "记录创建成功，AI分析正在生成中..."
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建记录失败: {str(e)}")

@router.get("/users/{user_id}/records/{record_date}", response_model=dict)
async def get_daily_record(user_id: int, record_date: str, db: Session = Depends(get_async_session)):
    """获取指定日期的记录"""
    record = await DailyRecordCRUD.get_daily_record(db, user_id, record_date)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 格式化返回数据
    record_data = {
        "id": record.id,
        "user_id": record.user_id,
        "record_date": record.record_date,
        "content": record.content,
        "mood_score": record.mood_score,
        "reflections": record.reflections,
        "work_activities": json.loads(record.work_activities) if record.work_activities else [],
        "personal_activities": json.loads(record.personal_activities) if record.personal_activities else [],
        "learning_activities": json.loads(record.learning_activities) if record.learning_activities else [],
        "health_activities": json.loads(record.health_activities) if record.health_activities else [],
        "goals_achieved": json.loads(record.goals_achieved) if record.goals_achieved else [],
        "challenges_faced": json.loads(record.challenges_faced) if record.challenges_faced else [],
        "created_at": record.created_at,
        "updated_at": record.updated_at
    }
    
    return record_data

@router.get("/users/{user_id}/records/", response_model=dict)
async def get_user_records(
    user_id: int, 
    skip: int = 0, 
    limit: int = 30,
    db: Session = Depends(get_async_session)
):
    """获取用户的记录列表"""
    records = await DailyRecordCRUD.get_user_records(db, user_id, skip, limit)
    
    records_data = []
    for record in records:
        record_data = {
            "id": record.id,
            "record_date": record.record_date,
            "content": record.content[:100] + "..." if len(record.content) > 100 else record.content,
            "mood_score": record.mood_score,
            "created_at": record.created_at
        }
        records_data.append(record_data)
    
    return {
        "total": len(records_data),
        "records": records_data
    }

@router.put("/users/{user_id}/records/{record_date}", response_model=dict)
async def update_daily_record(
    user_id: int, 
    record_date: str, 
    record_update: DailyRecordUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_async_session)
):
    """更新每日记录"""
    try:
        updated_record = await DailyRecordCRUD.update_daily_record(db, user_id, record_date, record_update)
        if not updated_record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 重新生成AI总结
        background_tasks.add_task(AISummaryCRUD.generate_ai_summary_task, db, user_id, updated_record.id)
        
        return {
            "id": updated_record.id,
            "record_date": updated_record.record_date,
            "updated_at": updated_record.updated_at,
            "message": "记录更新成功，AI分析正在重新生成中..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新记录失败: {str(e)}")

@router.delete("/users/{user_id}/records/{record_date}")
async def delete_daily_record(user_id: int, record_date: str, db: Session = Depends(get_async_session)):
    """删除每日记录"""
    success = await DailyRecordCRUD.delete_daily_record(db, user_id, record_date)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return {"message": "记录删除成功"}


@router.get("/users/{user_id}/today", response_model=dict)
async def get_today_info(user_id: int, db: Session = Depends(get_async_session)):
    """获取今日记录"""
    today = date.today().strftime('%Y-%m-%d')
    
    # 获取今日记录
    record = await DailyRecordCRUD.get_daily_record(db, user_id, today)
    record_data = None
    
    if record:
        record_data = {
            "id": record.id,
            "content": record.content,
            "mood_score": record.mood_score,
            "work_activities": json.loads(record.work_activities) if record.work_activities else [],
            "personal_activities": json.loads(record.personal_activities) if record.personal_activities else [],
            "learning_activities": json.loads(record.learning_activities) if record.learning_activities else [],
            "health_activities": json.loads(record.health_activities) if record.health_activities else [],
            "created_at": record.created_at
        }
    
    return {
        "date": today,
        "record": record_data,
        "has_record": record is not None,
    }