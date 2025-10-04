from typing import List, Optional
from pydantic import BaseModel
class DailyRecordCreate(BaseModel):
    content: str
    mood_score: Optional[int] = None
    work_activities: Optional[List[str]] = []
    personal_activities: Optional[List[str]] = []
    learning_activities: Optional[List[str]] = []
    health_activities: Optional[List[str]] = []
    goals_achieved: Optional[List[str]] = []
    challenges_faced: Optional[List[str]] = []
    reflections: Optional[str] = None

class DailyRecordUpdate(BaseModel):
    content: Optional[str] = None
    mood_score: Optional[int] = None
    work_activities: Optional[List[str]] = None
    personal_activities: Optional[List[str]] = None
    learning_activities: Optional[List[str]] = None
    health_activities: Optional[List[str]] = None
    goals_achieved: Optional[List[str]] = None
    challenges_faced: Optional[List[str]] = None
    reflections: Optional[str] = None
class DailyQuery(BaseModel):
    query: str