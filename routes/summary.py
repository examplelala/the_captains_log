# routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import json

from database import get_async_session
from crud.summary import AISummaryCRUD
from crud.record import DailyRecordCRUD


router = APIRouter()
@router.get("/users/{user_id}/summaries/{summary_date}", response_model=dict)
async def get_ai_summary(user_id: int, summary_date: str, db: Session = Depends(get_async_session)):
    """获取AI总结"""
    summary = await AISummaryCRUD.get_ai_summary(db, user_id, summary_date)
    if not summary:
        raise HTTPException(status_code=404, detail="AI总结不存在")
    
    summary_data = {
        "id": summary.id,
        "user_id": summary.user_id,
        "summary_date": summary.summary_date,
        "achievements_summary": summary.achievements_summary,
        "productivity_analysis": summary.productivity_analysis,
        "mood_analysis": summary.mood_analysis,
        "tomorrow_suggestions": json.loads(summary.tomorrow_suggestions) if summary.tomorrow_suggestions else [],
        "priority_tasks": json.loads(summary.priority_tasks) if summary.priority_tasks else [],
        "improvement_suggestions": json.loads(summary.improvement_suggestions) if summary.improvement_suggestions else [],
        "model_version": summary.model_version,
        "confidence_score": summary.confidence_score,
        "created_at": summary.created_at
    }
    
    return summary_data

@router.get("/users/{user_id}/summaries/", response_model=dict)
async def get_user_summaries(
    user_id: int, 
    skip: int = 0, 
    limit: int = 30,
    db: Session = Depends(get_async_session)
):
    """获取用户的AI总结列表"""
    summaries = await AISummaryCRUD.get_user_summaries(db, user_id, skip, limit)
    
    summaries_data = []
    for summary in summaries:
        summary_data = {
            "id": summary.id,
            "summary_date": summary.summary_date,
            "achievements_summary": summary.achievements_summary,
            "tomorrow_suggestions": json.loads(summary.tomorrow_suggestions) if summary.tomorrow_suggestions else [],
            "created_at": summary.created_at
        }
        summaries_data.append(summary_data)
    
    return {
        "total": len(summaries_data),
        "summaries": summaries_data
    }

@router.post("/users/{user_id}/records/{record_date}/regenerate-summary")
async def regenerate_ai_summary(
    user_id: int, 
    record_date: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_async_session)
):
    """重新生成AI总结"""
    record = await DailyRecordCRUD.get_daily_record(db, user_id, record_date)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    background_tasks.add_task(AISummaryCRUD.generate_ai_summary_task, db, user_id, record.id)
    
    return {"message": "AI总结正在重新生成中..."}

@router.get("/users/{user_id}/today", response_model=dict)
async def get_today_info(user_id: int, db: Session = Depends(get_async_session)):
    """获取今日AI总结"""
    today = date.today().strftime('%Y-%m-%d')
    

    summary = await AISummaryCRUD.get_ai_summary(db, user_id, today)
    summary_data = None
    
    if summary:
        summary_data = {
            "achievements_summary": summary.achievements_summary,
            "tomorrow_suggestions": json.loads(summary.tomorrow_suggestions) if summary.tomorrow_suggestions else [],
            "priority_tasks": json.loads(summary.priority_tasks) if summary.priority_tasks else [],
            "created_at": summary.created_at
        }
    
    return {
        "date": today,
        "ai_summary": summary_data,
        "has_summary": summary is not None
    }