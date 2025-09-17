# models/ai_data.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import json
from ._base import Base

import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base


class AISummary(Base):
    __tablename__ = 'ai_summaries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    daily_record_id = Column(Integer, ForeignKey('daily_records.id'), nullable=False, comment='关联的每日记录ID')

    achievements_summary = Column(Text, nullable=True, comment='成就总结')
    productivity_analysis = Column(Text, nullable=True, comment='生产力分析')
    mood_analysis = Column(Text, nullable=True, comment='情绪分析')
    tomorrow_suggestions = Column(Text, nullable=True, comment='明日建议 (JSON)')
    priority_tasks = Column(Text, nullable=True, comment='优先任务 (JSON)')
    improvement_suggestions = Column(Text, nullable=True, comment='改进建议 (JSON)')
    model_version = Column(String(50), nullable=True, comment='AI模型版本')
    confidence_score = Column(Integer, nullable=True, comment='AI置信度评分')

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc),
                        onupdate=datetime.now(timezone.utc), comment='更新时间')

    user = relationship("User", back_populates="ai_summaries")
    daily_record = relationship("DailyRecord", back_populates="ai_summary")

    def set_suggestions(self, suggestions_list):
        self.tomorrow_suggestions = json.dumps(suggestions_list, ensure_ascii=False)

    def get_suggestions(self):
        return json.loads(self.tomorrow_suggestions) if self.tomorrow_suggestions else []

    def set_priority_tasks(self, tasks_list):
        self.priority_tasks = json.dumps(tasks_list, ensure_ascii=False)

    def get_priority_tasks(self):
        return json.loads(self.priority_tasks) if self.priority_tasks else []

    def set_improvement_suggestions(self, suggestions_list):
        self.improvement_suggestions = json.dumps(suggestions_list, ensure_ascii=False)

    def get_improvement_suggestions(self):
        return json.loads(self.improvement_suggestions) if self.improvement_suggestions else []


class AIAnalysisLog(Base):
    __tablename__ = 'ai_analysis_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    daily_record_id = Column(Integer, ForeignKey('daily_records.id'), nullable=False, comment='关联的每日记录ID')

    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), comment='创建时间')