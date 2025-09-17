# models/user.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ._base import Base 

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    email = Column(String(100), unique=True, nullable=True, comment='邮箱')
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment='更新时间')
    is_active = Column(Boolean, default=True, comment='是否激活')

    daily_records = relationship("DailyRecord", back_populates="user", cascade="all, delete-orphan")
    ai_summaries = relationship("AISummary", back_populates="user", cascade="all, delete-orphan")
    user_settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False, comment='用户ID')

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment='更新时间')
    user = relationship("User", back_populates="user_settings")