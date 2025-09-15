from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
import json
from ._base import Base 

class TaskTemplate(Base):
    __tablename__ = 'task_templates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')

    created_at = Column(DateTime, default=datetime.now(timezone.utc), comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), comment='更新时间')

    def set_template_data(self, template_data):
        self.template_content = json.dumps(template_data, ensure_ascii=False)

    def get_template_data(self):
        return json.loads(self.template_content) if self.template_content else {}