from __future__ import annotations

from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import settings


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model_name,
        temperature=0.7,
    )


def build_prompt_no_rag() -> ChatPromptTemplate:
    system = (
        "你是智能助手，专门帮用户分析问题并提供基于数据的回答。"
        "你的首要任务是准确回答用户的具体问题，然后提供支撑信息。\n\n"
        "回答原则：\n"
        "1. 直接回答用户问题\n"
        "2. 基于记录数据给出证据\n"
        "3. 提供相关洞察（可选）\n"
        "4. 明确数据来源\n\n"
        "格式要求：\n"
        "- answer: 直接回答用户问题（1-3句）\n"
        "- evidence: 支撑证据（2-4条）\n"
        "- insights: 相关洞察（可选，0-3条）\n"
        "- sources: 数据来源\n"
        "- confidence: 置信度（高/中/低）"
    )
    user = (
        "用户问题：{query}\n\n"
        "基于以下单日记录回答：\n"
        "日期: {record_date}\n"
        "内容: {content}\n"
        "心情: {mood_score}\n"
        "反思: {reflections}\n"
        "工作: {work_activities}\n"
        "个人: {personal_activities}\n"
        "学习: {learning_activities}\n"
        "健康: {health_activities}\n"
        "目标: {goals_achieved}\n"
        "挑战: {challenges_faced}\n\n"
        "输出JSON格式：\n\n"
        "answer: 直接回答用户问题\n"
        "evidence: [\"证据1\", \"证据2\"] - 支撑回答的具体事实\n"
        "insights: [\"洞察1\", \"洞察2\"] - 可选的额外洞察\n"
        "sources: [\"单日记录: {record_date}\"] - 数据来源\n"
        "confidence: \"高\"|\"中\"|\"低\" - 回答置信度"
    )
    return ChatPromptTemplate.from_messages([("system", system), ("user", user)])


def build_prompt_with_history() -> ChatPromptTemplate:
    system = (
        "你是专业数据分析师，擅长处理历史数据并回答用户问题。"
        "你的首要任务是准确回答用户的具体问题，然后做数据支撑。\n\n"
        "分析原则：\n"
        "1. 直接回答用户问题\n"
        "2. 基于历史数据分析趋势\n"
        "3. 提供数据证据支撑\n"
        "4. 列出相关记录来源\n\n"
        "格式要求：\n"
        "- answer: 直接回答用户问题（基于历史数据）\n"
        "- trend_analysis: 基于数据的趋势分析（2-4条）\n"
        "- evidence: 支撑回答的具体证据（2-4条）\n"
        "- sources: 引用的记录来源\n"
        "- confidence: 置信度（高/中/低）"
    )
    user = (
        "用户问题：{query}\n\n"
        "相关历史记录：\n"
        "{history}\n\n"
        "输出JSON格式：\n\n"
        "answer: 基于历史数据直接回答用户问题\n"
        "trend_analysis: [\"趋势1\", \"趋势2\"] - 数据趋势分析\n"
        "evidence: [\"证据1\", \"证据2\"] - 支撑回答的事实\n"
        "sources: [\"[src:id,sim]记录片段\"] - 数据来源及相似度\n"
        "confidence: \"高\"|\"中\"|\"低\" - 回答置信度"
    )
    return ChatPromptTemplate.from_messages([("system", system), ("user", user)])


def build_prompt_intent() -> ChatPromptTemplate:
    system = (
        "你是一个意图分类器，负责把用户的问题分到以下四类之一：\n"
        "1. today_summary：明确只查询今天的数据，如含“今天”“今日”“今早”“刚刚”“今天上午”等字样或语境。\n"
        "2. recent_summary：指近几天（通常7天内）的问题，如“最近”“前几天”“过去几天”“上周”等，或者用户未指定具体日期但问题指向近期。\n"
        "3. cross_days_trend：跨更长时间段（大约30天及以上）或需要比较趋势、统计走势、长期变化时选择，如“最近一个月趋势”“这几周变化”“长期变化”“增长趋势”。\n"
        "4. general_qa：不限时间范围或与日期无关的常规问答，如“谁创建了这个记录”“内容里有没有提到XXX”或需要查看全部历史数据。\n\n"
        "分类规则：\n"
        "- 必须只输出这四个标签之一，全小写，不加解释，不加标点。\n"
        "- 如果问题指向当天则选today_summary。\n"
        "- 如果用户提到‘前几天’‘最近几天’或没有明确日期，但看起来是想看近期记录，则选recent_summary。\n"
        "- 如果问题较复杂，需要比较或分析趋势、涉及更长时间段(>7天)再选cross_days_trend。\n"
        "- 如果问题与时间无关或显然需要全量数据则选general_qa。\n"
        "- 不确定时优先选recent_summary，不要直接跳到cross_days_trend或general_qa。\n"
        "- 例子：\n"
        "  用户问“今天的心情记录是什么” → today_summary\n"
        "  用户问“我因为什么什么生气的那一天是哪一天” → recent_summary\n"
        "  用户问“最近一个月我体重变化趋势” → cross_days_trend\n"
        "  用户问“谁写下了这条备注” → general_qa\n"
    )
    user = "用户问题：{query}"
    return ChatPromptTemplate.from_messages([("system", system), ("user", user)])


def build_relevance_check_prompt() -> ChatPromptTemplate:
    """构建LLM相关性判断的prompt"""
    return ChatPromptTemplate.from_messages([
        ("system", """你是一个数据相关性判断专家。你的任务是判断检索到的日记记录是否能够回答用户的问题。

判断标准：
1. 内容相关性：记录内容是否涉及问题的主题
2. 信息完整性：是否有足够的信息来回答问题
3. 时间合理性：时间范围是否符合问题意图

返回JSON格式：
{{
    "can_answer": true/false,
    "confidence": "高/中/低",
    "reason": "判断理由",
    "missing_info": "如果不能回答，缺少什么信息"
}}

如果记录完全无关或信息严重不足，返回 can_answer: false
如果有一定相关性但信息不够完整，返回 can_answer: true 但 confidence: "低"
如果内容相关且信息较完整，返回 can_answer: true 且 confidence: "高"
"""),
        ("user", """用户问题：{query}

检索到的记录：
{records_summary}

请判断这些记录是否足以回答用户的问题。""")
    ])
