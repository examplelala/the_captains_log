
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from ._base import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import Index
class DailyRecord(Base):
    __tablename__ = 'daily_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    record_date = Column(String(10), nullable=False, comment='记录日期(YYYY-MM-DD)')
    content = Column(Text, nullable=True, comment='记录内容')
    mood_score = Column(Integer, nullable=True, comment='心情评分')
    reflections = Column(Text, nullable=True, comment='反思')
    work_activities = Column(Text, nullable=True, comment='工作活动 (JSON)')
    personal_activities = Column(Text, nullable=True, comment='个人活动 (JSON)')
    learning_activities = Column(Text, nullable=True, comment='学习活动 (JSON)')
    health_activities = Column(Text, nullable=True, comment='健康活动 (JSON)')
    goals_achieved = Column(Text, nullable=True, comment='实现目标 (JSON)')
    challenges_faced = Column(Text, nullable=True, comment='面临挑战 (JSON)')
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment='更新时间')
    user = relationship("User", back_populates="daily_records")
    ai_summary = relationship("AISummary", back_populates="daily_record", uselist=False, cascade="all, delete-orphan")
    vector = Column(Vector(512), nullable=True, comment='向量嵌入')
    __table_args__ = (Index(
            'idx_daily_records_vector',
            'vector',
            postgresql_using='ivfflat'  # 或 'hnsw'
        ),
        {'comment': '每日记录表'})

    def set_activities(self, category, activities_list):
        if hasattr(self, f'{category}_activities'):
            setattr(self, f'{category}_activities', json.dumps(activities_list, ensure_ascii=False))

    def get_activities(self, category):
        activities_json = getattr(self, f'{category}_activities')
        return json.loads(activities_json) if activities_json else []