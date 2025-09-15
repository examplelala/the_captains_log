
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import json

from database import get_async_session
from crud.user import UserCRUD
from schemas.user import UserCreate

router = APIRouter()
@router.post("/users/", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_async_session)):
    """创建新用户"""
    try:
        # 检查用户名是否已存在
        existing_user = await UserCRUD.get_user_by_username(db, user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        db_user = await UserCRUD.create_user(db, user)
        return {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "created_at": db_user.created_at,
            "message": "用户创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@router.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: int, db: Session = Depends(get_async_session)):
    """获取用户信息"""
    user = await UserCRUD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "is_active": user.is_active
    }