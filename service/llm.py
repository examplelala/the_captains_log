# ai_service.py
from typing import List
from click import prompt
from openai import AsyncOpenAI
import json
from typing import Dict, Any
from config import settings
from schemas.record import DailyRecordCreate
from utils.logger import logger
from datetime import date
class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        self.model = settings.llm_model_name
    
    async def analyze_daily_content(self, content: str) -> DailyRecordCreate:
        prompt = f"""
你是一个信息抽取助手。你的任务是从输入文本（content）中提取信息，填充到 DailyRecordCreate 类型的 JSON 对象中。

DailyRecordCreate 类型定义如下：

  "content": str,  // 原始输入文本
  "mood_score": Optional[int],  // 提到心情的分数或程度（如 1-10），否则为 null
  "work_activities": Optional[List[str]],  // 提到的工作相关活动（如“写报告”、“开会”）
  "personal_activities": Optional[List[str]],  // 提到的个人休闲活动（如“看电影”、“散步”）
  "learning_activities": Optional[List[str]],  // 提到的学习相关活动（如“读书”、“写作业”）
  "health_activities": Optional[List[str]],  // 提到的健康活动（如“跑步”、“健身”、“睡眠”）
  "goals_achieved": Optional[List[str]],  // 提到的已完成目标
  "challenges_faced": Optional[List[str]],  // 提到的遇到的困难或挑战
  "reflections": Optional[str]  // 个人总结、反思、感悟


要求：
1. 仅从输入 content 中提取信息，不要编造。
2. 如果某个字段没有相关信息，请保持为 null 或空数组（[]）。
3. 保持 JSON 输出格式正确，确保键名和类型完全符合 DailyRecordCreate。
4. 输出中必须包含 "content" 原始文本。

输入示例：
content: "今天心情7分，上午写了一份报告，晚上和朋友去看电影。"

输出示例：
{{
  "content": "今天心情7分，上午写了一份报告，晚上和朋友去看电影。",
  "mood_score": 7,
  "work_activities": ["写了一份报告"],
  "personal_activities": ["看电影"],
  "learning_activities": [],
  "health_activities": [],
  "goals_achieved": [],
  "challenges_faced": [],
  "reflections": null
}}
原始的输入文本为：{content}
    """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的信息提取助手，请从提供的文本中提取结构化信息，并以JSON格式返回。只返回有信息的字段。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # 降低温度，以获得更准确的提取结果
                max_tokens=800
            )
            
            content_response = response.choices[0].message.content
            try:
                cleaned = content_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[len("```json"):].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()
                extracted_data = json.loads(cleaned)
                record = DailyRecordCreate(**extracted_data)
                return record
            except json.JSONDecodeError:
                logger.error(f"无法解析JSON：{content_response}")
                raise
                
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.error(f"当前{content_response}")
            raise


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
                cleaned = content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[len("```json"):].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()
                summary_data = json.loads(cleaned)
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
    
    # 在 ai_service 中新增方法
    async def generate_daily_summary_with_history(self, records_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于历史记录生成AI总结"""
        prompt = self._build_summary_prompt_with_history(records_data)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的生活助手，帮助用户分析多日活动趋势并提供个性化建议。请用中文回复，格式要求为JSON。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000  # 增加token限制，因为要处理更多数据
            )
            
            content = response.choices[0].message.content
            
            try:
                cleaned = content.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[len("```json"):].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()
                summary_data = json.loads(cleaned)
            except json.JSONDecodeError:
                # 返回默认分析
                current_record = records_data[-1] if records_data else {}
                summary_data = {
                    "achievements_summary": content[:500] if content else "AI分析暂时不可用",
                    "productivity_analysis": "需要更多数据进行分析",
                    "mood_analysis": f"心情评分: {current_record.get('mood_score', '未评分')}",
                    "tomorrow_suggestions": ["继续保持良好习惯", "关注未完成的任务"],
                    "priority_tasks": ["回顾重要任务", "制定明日计划"],
                    "improvement_suggestions": ["保持记录习惯", "注意工作生活平衡"]
                }
            
            # 添加AI模型信息
            summary_data.update({
                "model_version": self.model,
                "confidence_score": 85,
                "summary_date": date.today().strftime('%Y-%m-%d')
            })
            
            return summary_data
            
        except Exception as e:
            print(f"AI分析出错: {str(e)}")
            current_record = records_data[-1] if records_data else {}
            return self._get_default_summary(current_record)
    def _build_summary_prompt_with_history(self, records_data: List[Dict[str, Any]]) -> str:
        """构建基于历史数据的AI分析prompt"""
        
        if not records_data:
            return self._build_summary_prompt({})
        
        # ===== 新增：按日期分组聚合记录 =====
        daily_aggregated = {}
        for record in records_data:
            date = record.get('record_date')
            if date not in daily_aggregated:
                daily_aggregated[date] = {
                    'record_date': date,
                    'contents': [],
                    'mood_scores': [],
                    'reflections': [],
                    'work_activities': [],
                    'personal_activities': [],
                    'learning_activities': [],
                    'health_activities': [],
                    'goals_achieved': [],
                    'challenges_faced': []
                }
            
            # 聚合数据
            daily_data = daily_aggregated[date]
            if record.get('content'):
                daily_data['contents'].append(record['content'])
            if record.get('mood_score'):
                daily_data['mood_scores'].append(record['mood_score'])
            if record.get('reflections'):
                daily_data['reflections'].append(record['reflections'])
            
            # 聚合活动数据
            daily_data['work_activities'].extend(record.get('work_activities', []))
            daily_data['personal_activities'].extend(record.get('personal_activities', []))
            daily_data['learning_activities'].extend(record.get('learning_activities', []))
            daily_data['health_activities'].extend(record.get('health_activities', []))
            daily_data['goals_achieved'].extend(record.get('goals_achieved', []))
            daily_data['challenges_faced'].extend(record.get('challenges_faced', []))
        
        # 按日期排序
        sorted_dates = sorted(daily_aggregated.keys())
        
        # 构建历史趋势分析
        history_analysis = ""
        mood_scores_by_day = []
        all_activities = {
            'work': [], 'personal': [], 'learning': [], 'health': []
        }
        
        for date in sorted_dates:
            daily_data = daily_aggregated[date]
            history_analysis += f"\n=== {date} ===\n"
            
            # 处理多条记录的内容
            if daily_data['contents']:
                history_analysis += f"记录内容({len(daily_data['contents'])}条):\n"
                for i, content in enumerate(daily_data['contents'], 1):
                    history_analysis += f"  {i}. {content}\n"
            
            # 处理心情评分（多条取平均）
            if daily_data['mood_scores']:
                avg_mood = sum(daily_data['mood_scores']) / len(daily_data['mood_scores'])
                mood_range = f"{min(daily_data['mood_scores'])}-{max(daily_data['mood_scores'])}" if len(daily_data['mood_scores']) > 1 else str(daily_data['mood_scores'][0])
                history_analysis += f"心情评分: {avg_mood:.1f}/10 (范围: {mood_range})\n"
                mood_scores_by_day.append(avg_mood)
            else:
                history_analysis += f"心情评分: 未评分\n"
            
            # 去重后的活动统计
            work_unique = list(set(daily_data['work_activities']))
            personal_unique = list(set(daily_data['personal_activities']))
            learning_unique = list(set(daily_data['learning_activities']))
            health_unique = list(set(daily_data['health_activities']))
            
            if work_unique:
                history_analysis += f"工作活动: {', '.join(work_unique)}\n"
                all_activities['work'].extend(work_unique)
            if personal_unique:
                history_analysis += f"个人活动: {', '.join(personal_unique)}\n"
                all_activities['personal'].extend(personal_unique)
            if learning_unique:
                history_analysis += f"学习活动: {', '.join(learning_unique)}\n"
                all_activities['learning'].extend(learning_unique)
            if health_unique:
                history_analysis += f"健康活动: {', '.join(health_unique)}\n"
                all_activities['health'].extend(health_unique)
            
            # 目标和挑战
            goals_unique = list(set(daily_data['goals_achieved']))
            challenges_unique = list(set(daily_data['challenges_faced']))
            
            if goals_unique:
                history_analysis += f"完成目标: {', '.join(goals_unique)}\n"
            if challenges_unique:
                history_analysis += f"遇到挑战: {', '.join(challenges_unique)}\n"
            
            # 反思合并
            if daily_data['reflections']:
                history_analysis += f"反思总结: {' | '.join(daily_data['reflections'])}\n"
        
        # 趋势统计
        trend_info = ""
        if mood_scores_by_day:
            avg_mood = sum(mood_scores_by_day) / len(mood_scores_by_day)
            if len(mood_scores_by_day) > 1:
                mood_trend = "上升" if mood_scores_by_day[-1] > mood_scores_by_day[0] else "稳定" if mood_scores_by_day[-1] == mood_scores_by_day[0] else "下降"
            else:
                mood_trend = "稳定"
            trend_info += f"心情趋势: 平均 {avg_mood:.1f}分，呈{mood_trend}趋势\n"
        
        # 活动频次统计（去重）
        activity_summary = ""
        for category, activities in all_activities.items():
            if activities:
                unique_activities = list(set(activities))
                category_name = {'work': '工作', 'personal': '个人', 'learning': '学习', 'health': '健康'}[category]
                activity_summary += f"{category_name}活动: {len(unique_activities)}种不同活动\n"
        
        # 计算记录密度
        total_records = len(records_data)
        total_days = len(sorted_dates)
        record_density = total_records / total_days if total_days > 0 else 0

        prompt = f"""
    请基于以下用户的多日记录进行综合分析，提供个性化的总结和建议：

    === 数据概览 ===
    分析期间: {total_days} 天，共 {total_records} 条记录
    记录密度: 平均每天 {record_density:.1f} 条记录
    {trend_info}

    === 活动统计 ===
    {activity_summary}

    === 详细记录 ===
    {history_analysis}

    === 分析要求 ===
    请结合历史趋势，重点分析：
    1. 多条记录反映的日常节奏和记录习惯
    2. 情绪在一天内的变化模式和影响因素
    3. 活动类型的多样性和平衡性
    4. 目标完成的一致性和持续性
    5. 记录频率对自我管理的影响

    请返回以下JSON格式的分析：
    {{
        "achievements_summary": "基于多日多条记录的成就总结，体现记录习惯的价值（150字以内）",
        "productivity_analysis": "效率趋势分析，包含记录频率对效率的影响（150字以内）", 
        "mood_analysis": "情绪模式分析，包含日内波动和日间趋势（150字以内）",
        "tomorrow_suggestions": ["基于历史记录模式的具体建议1", "建议2", "建议3"],
        "priority_tasks": ["根据历史记录频率和内容的优先事项1", "优先事项2", "优先事项3"],
        "improvement_suggestions": ["基于多条记录观察的记录和生活改进建议1", "改进建议2"]
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