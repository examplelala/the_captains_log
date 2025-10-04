from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, text

from models.daily_record import DailyRecord
from service.embedding import generate_vectors
from agents.langgraph.state import AgentState
from agents.langgraph.llm import get_llm, build_prompt_no_rag, build_prompt_with_history, build_prompt_intent


def _classify_intent(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["今天总结", "今日总结", "今天建议", "今日建议", "今天的总结", "今天的建议"]):
        return "today_summary"
    if any(k in t for k in ["过去一周", "上周", "近一周", "7天", "一周"]):
        return "recent_summary"
    if any(k in t for k in ["趋势", "跨日", "多日", "这段时间", "最近一段时间", "生产力", "情绪趋势"]):
        return "cross_days_trend"
    return "general_qa"


async def classify_intent_node(state: AgentState) ->dict:
    llm = get_llm()
    prompt = build_prompt_intent()
    chain = prompt | llm
    resp = await chain.ainvoke({"query": state.get("query", "")})
    label = (resp.content or "").strip().lower()
    if label not in {"today_summary", "recent_summary", "cross_days_trend", "general_qa"}:
        label = _classify_intent(state.get("query", ""))
    return {"intent": label}


def _parse_time_range(intent: str) -> (Optional[str], Optional[str]):
    today = date.today()
    if intent == "today_summary":
        d = today.strftime("%Y-%m-%d")
        return d, d
    if intent == "recent_summary":
        return (today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    if intent == "cross_days_trend":
        return (today - timedelta(days=30)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    return None, None


async def time_range_node(state: AgentState) -> dict:
    start_date, end_date = _parse_time_range(state.get("intent", ""))
    return {"start_date": start_date, "end_date": end_date}


async def prefilter_node(state: AgentState, session: AsyncSession) -> dict:
    user_id = state["user_id"]
    conditions = [DailyRecord.user_id == user_id]
    if state.get("start_date"):
        conditions.append(DailyRecord.record_date >= state["start_date"]) 
    if state.get("end_date"):
        conditions.append(DailyRecord.record_date <= state["end_date"]) 

    stmt = (
        select(DailyRecord)
        .where(and_(*conditions))
        .order_by(desc(DailyRecord.record_date))
        .limit(200)
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    candidates = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "record_date": r.record_date,
            "content": r.content,
            "mood_score": r.mood_score,
            "reflections": r.reflections,
            "work_activities": r.work_activities,
            "personal_activities": r.personal_activities,
            "learning_activities": r.learning_activities,
            "health_activities": r.health_activities,
            "goals_achieved": r.goals_achieved,
            "challenges_faced": r.challenges_faced,
        }
        for r in rows
    ]

    return {"candidates": candidates}


def need_rag(state: AgentState) -> bool:
    return state.get("intent") in {"recent_summary", "cross_days_trend"}


def _validate_and_fix_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证并修复响应数据格式"""
    # 检查是否为新的answer格式还是旧的summary格式
    if "answer" in data:
        # 新格式 - 以回答query为主
        result = {
            "answer": data.get("answer", "无法回答"),
            "evidence": data.get("evidence", []),
            "trend_analysis": data.get("trend_analysis", []),
            "insights": data.get("insights", []),
            "sources": data.get("sources", []),
            "confidence": data.get("confidence", "中")
        }
        
        # 确保字段类型正确
        if not isinstance(result["evidence"], list):
            result["evidence"] = [str(result["evidence"])]
        if not isinstance(result["trend_analysis"], list):
            result["trend_analysis"] = [str(result["trend_analysis"])]
        if not isinstance(result["insights"], list):
            result["insights"] = [str(result["insights"])]
            
    else:
        # 旧格式 - 兼容处理
        result = {
            "answer": data.get("summary", "分析完成"),
            "evidence": data.get("key_insights", ["无特别洞察"]),
            "trend_analysis": data.get("productivity_analysis", ["继续现有计划"]),
            "insights": data.get("improvement_suggestions", ["持续改进"]),
            "sources": data.get("sources", []),
            "confidence": data.get("confidence", "中")
        }
        
        # 确保字段类型正确
        if not isinstance(result["evidence"], list):
            result["evidence"] = [str(result["evidence"])]
        if not isinstance(result["insights"], list):
            result["insights"] = [str(result["insights"])]
    
    if not isinstance(result["trend_analysis"], list):
        result["trend_analysis"] = [str(result["trend_analysis"])]
    if not isinstance(result["sources"], list):
        result["sources"] = []
    
    # 验证置信度
    if result["confidence"] not in ["高", "中", "低"]:
        result["confidence"] = "中"
    
    return result


def _parse_json_response(raw_response: str) -> Dict[str, Any]:
    """解析LLM返回的JSON响应，处理包裹在```json```中的内容"""
    content = raw_response.strip()
    
    # 尝试提取```json```包裹的内容
    if "```json" in content:
        try:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                json_str = content[start:end].strip()
                return _validate_and_fix_response(json.loads(json_str))
        except (json.JSONDecodeError, ValueError):
            pass
    
    # 尝试提取简单```包裹的内容
    elif content.startswith("```") and content.endswith("```"):
        try:
            json_str = content[3:-3].strip()
            return _validate_and_fix_response(json.loads(json_str))
        except (json.JSONDecodeError, ValueError):
            pass
    
    # 直接尝试解析整个内容为JSON
    try:
        return _validate_and_fix_response(json.loads(content))
    except (json.JSONDecodeError, ValueError):
        pass
    
    # 如果无法解析为JSON，返回默认结构
    return {
        "answer": "解析失败，请重新生成结构化结果",
        "evidence": ["重新生成更结构化的结果"],
        "trend_analysis": ["修复结果格式"],
        "insights": ["检查数据格式"],
        "sources": [],
        "confidence": "低"
    }


async def embed_node(state: AgentState) -> dict:
    qv = generate_vectors(state.get("query", ""))
    return {"query_vector": qv}


async def retrieve_node(state: AgentState, session: AsyncSession) -> dict:
    qv = state.get("query_vector")
    if not qv:
        return {"retrieved": state.get("candidates", [])}

    vector_str = "[" + ",".join(map(str, qv)) + "]"
    filters = ["user_id = :user_id", "vector IS NOT NULL"]
    if state.get("start_date"):
        filters.append("record_date >= :start_date")
    if state.get("end_date"):
        filters.append("record_date <= :end_date")
    where_sql = " AND ".join(filters)
    sql = f"""
        SELECT id, user_id, record_date, content, mood_score, reflections,
               (1 - (vector <=> (:qv)::vector)) AS similarity
        FROM daily_records
        WHERE {where_sql}
        ORDER BY vector <=> (:qv)::vector
        LIMIT :top_k
    """
    params: Dict[str, Any] = {
        "user_id": state["user_id"],
        "qv": vector_str,
        "top_k": 10,
    }
    if state.get("start_date"):
        params["start_date"] = state["start_date"]
    if state.get("end_date"):
        params["end_date"] = state["end_date"]

    result = await session.execute(text(sql), params)
    rows = result.fetchall()
    retrieved = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "record_date": r.record_date,
            "content": r.content,
            "mood_score": r.mood_score,
            "reflections": r.reflections,
            "similarity": float(r.similarity) if r.similarity is not None else None,
        }
        for r in rows
    ]

    return {"retrieved": retrieved}


async def generate_no_rag_node(state: AgentState) -> dict:
    candidates = state.get("candidates", [])
    latest = candidates[0] if candidates else {}
    payload: Dict[str, Any] = {
        "query": state.get("query", ""),
        "record_date": latest.get("record_date"),
        "content": latest.get("content", ""),
        "mood_score": latest.get("mood_score"),
        "reflections": latest.get("reflections"),
        "work_activities": latest.get("work_activities"),
        "personal_activities": latest.get("personal_activities"),
        "learning_activities": latest.get("learning_activities"),
        "health_activities": latest.get("health_activities"),
        "goals_achieved": latest.get("goals_achieved"),
        "challenges_faced": latest.get("challenges_faced"),
    }
    llm = get_llm()
    prompt = build_prompt_no_rag()
    chain = prompt | llm
    resp = await chain.ainvoke(payload)
    
    # 解析JSON响应为结构化数据
    parsed_data = _parse_json_response(resp.content)
    
    return {
        "result": {
            "used_rag": False,
            "data": parsed_data,
        }
    }


async def generate_with_history_node(state: AgentState) -> dict:
    records = state.get("retrieved") or state.get("candidates") or []
    simplified = [
        {
            "record_date": r.get("record_date"),
            "content": r.get("content"),
            "mood_score": r.get("mood_score"),
            "reflections": r.get("reflections"),
        }
        for r in records
    ]
    history = "\n".join(
        [f"{r.get('record_date')}: {r.get('content')[:200] if r.get('content') else ''}" for r in simplified]
    )
    llm = get_llm()
    prompt = build_prompt_with_history()
    chain = prompt | llm
    resp = await chain.ainvoke({"query": state.get("query", ""), "history": history})
    
    # 解析JSON响应为结构化数据
    parsed_data = _parse_json_response(resp.content)
    
    return {
        "result": {
            "used_rag": True,
            "data": parsed_data
        }
    }


