# ai_service.py
import os
from openai import AsyncOpenAI
import json
from typing import Dict, Any
from config import settings

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        self.model = settings.llm_model_name
    
    async def generate_daily_summary(self, daily_record: Dict[str, Any]) -> Dict[str, Any]:
        """基于每日记录生成AI总结和明日建议"""
        
 
        prompt = self._build_summary_prompt(daily_record)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的生活助手，帮助用户分析每日活动并提供明日建议。请用中文回复，格式要求为JSON。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            

            try:
                summary_data = json.loads(content)
            except json.JSONDecodeError:
                # 返回默认分析
                summary_data = {
                    "achievements_summary": content[:500] if content else "AI分析暂时不可用",
                    "productivity_analysis": "需要更多数据进行分析",
                    "mood_analysis": f"心情评分: {daily_record.get('mood_score', '未评分')}",
                    "tomorrow_suggestions": ["继续保持今日的良好习惯", "关注未完成的任务"],
                    "priority_tasks": ["回顾今日重要任务", "制定明日计划"],
                    "improvement_suggestions": ["保持记录习惯", "注意工作生活平衡"]
                }
            
            # 添加AI模型信息
            summary_data.update({
                "model_version": self.model,
                "confidence_score": 85  # 固定置信度，实际应用中可以动态计算
            })
            
            return summary_data
            
        except Exception as e:
            print(f"AI分析出错: {str(e)}")
            # 返回默认分析
            return self._get_default_summary(daily_record)
    
    def _build_summary_prompt(self, daily_record: Dict[str, Any]) -> str:
        """构建AI分析的prompt"""
        
        activities_text = ""
        if daily_record.get('work_activities'):
            activities_text += f"工作活动: {', '.join(daily_record['work_activities'])}\n"
        if daily_record.get('personal_activities'):
            activities_text += f"个人活动: {', '.join(daily_record['personal_activities'])}\n"
        if daily_record.get('learning_activities'):
            activities_text += f"学习活动: {', '.join(daily_record['learning_activities'])}\n"
        if daily_record.get('health_activities'):
            activities_text += f"健康活动: {', '.join(daily_record['health_activities'])}\n"
        
        goals_text = ""
        if daily_record.get('goals_achieved'):
            goals_text += f"完成的目标: {', '.join(daily_record['goals_achieved'])}\n"
        if daily_record.get('challenges_faced'):
            goals_text += f"遇到的挑战: {', '.join(daily_record['challenges_faced'])}\n"
        
        prompt = f"""
请分析以下每日记录，并提供JSON格式的回复：

日期: {daily_record.get('record_date', '今日')}
心情评分: {daily_record.get('mood_score', '未评分')}/10
主要内容: {daily_record.get('content', '')}

活动记录:
{activities_text}

目标和挑战:
{goals_text}

反思总结: {daily_record.get('reflections', '无')}

请返回以下JSON格式的分析：
{{
    "achievements_summary": "今日成就总结（100字以内）",
    "productivity_analysis": "效率分析（100字以内）", 
    "mood_analysis": "情绪分析（100字以内）",
    "tomorrow_suggestions": ["建议1", "建议2", "建议3"],
    "priority_tasks": ["优先任务1", "优先任务2", "优先任务3"],
    "improvement_suggestions": ["改进建议1", "改进建议2"]
}}
"""
        return prompt
    
    def _get_default_summary(self, daily_record: Dict[str, Any]) -> Dict[str, Any]:
        """当AI服务不可用时的默认分析"""
        mood_score = daily_record.get('mood_score')
        mood_text = f"心情评分 {mood_score}/10" if mood_score else "心情状态良好"
        
        return {
            "achievements_summary": f"今日完成了记录，{mood_text}，继续保持记录习惯。",
            "productivity_analysis": "基于记录内容，建议继续保持当前的工作节奏。",
            "mood_analysis": mood_text,
            "tomorrow_suggestions": ["继续记录每日活动", "关注重要任务的完成", "保持良好心态"],
            "priority_tasks": ["制定明日计划", "回顾今日未完成任务"],
            "improvement_suggestions": ["保持记录习惯", "注意工作生活平衡"],
            "model_version": "default",
            "confidence_score": 60
        }

ai_service = AIService()