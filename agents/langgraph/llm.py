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
        "你是一个意图分类器。根据用户的问题判断任务类型，并且只输出一个标签。"
        "可选标签: today_summary, recent_summary, cross_days_trend, general_qa。"
        "必须只输出上述标签之一，全部小写，不要多余文字。"
    )
    user = "用户问题：{query}"
    return ChatPromptTemplate.from_messages([("system", system), ("user", user)])


