
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from ._base import Base

class DailyRecord(Base):
    __tablename__ = 'daily_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    record_date = Column(String(10), nullable=False, comment='记录日期(YYYY-MM-DD)')
    created_at = Column(DateTime, default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment='更新时间')
    user = relationship("User", back_populates="daily_records")
    ai_summary = relationship("AISummary", back_populates="daily_record", uselist=False, cascade="all, delete-orphan")
    __table_args__ = ({'comment': '每日记录表'},)

    def set_activities(self, category, activities_list):
        if hasattr(self, f'{category}_activities'):
            setattr(self, f'{category}_activities', json.dumps(activities_list, ensure_ascii=False))

    def get_activities(self, category):
        activities_json = getattr(self, f'{category}_activities')
        return json.loads(activities_json) if activities_json else []