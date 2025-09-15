# models/ai_data.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from ._base import Base

class AISummary(Base):
    __tablename__ = 'ai_summaries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    daily_record_id = Column(Integer, ForeignKey('daily_records.id'), nullable=False, comment='关联的每日记录ID')

    created_at = Column(DateTime, default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment='更新时间')
    user = relationship("User", back_populates="ai_summaries")
    daily_record = relationship("DailyRecord", back_populates="ai_summary")

    def set_suggestions(self, suggestions_list):
        self.tomorrow_suggestions = json.dumps(suggestions_list, ensure_ascii=False)

    def get_suggestions(self):
        return json.loads(self.tomorrow_suggestions) if self.tomorrow_suggestions else []

class AIAnalysisLog(Base):
    __tablename__ = 'ai_analysis_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    daily_record_id = Column(Integer, ForeignKey('daily_records.id'), nullable=False, comment='关联的每日记录ID')

    created_at = Column(DateTime, default=datetime.now(timezone.utc), comment='创建时间')