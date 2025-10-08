from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, timedelta
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, text, func, cast,literal_column
from utils.logger import logger
from models.daily_record import DailyRecord
from service.embedding import generate_vectors
from agents.langgraph.state import AgentState
from agents.langgraph.llm import get_llm, build_prompt_no_rag, build_prompt_with_history, build_prompt_intent,build_relevance_check_prompt
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.sql import text as sql_text

def _classify_intent(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["今天总结", "今日总结", "今天建议", "今日建议", "今天的总结", "今天的建议"]):
        return "today_summary"
    if any(k in t for k in ["过去一周", "上周", "近一周", "7天", "一周"]):
        return "recent_summary"
    if any(k in t for k in ["趋势", "跨日", "多日", "这段时间", "最近一段时间", "生产力", "情绪趋势"]):
        return "cross_days_trend"
    return "general_qa"


async def classify_intent_node(state: AgentState) -> dict:
    llm = get_llm()
    prompt = build_prompt_intent()
    chain = prompt | llm
    resp = await chain.ainvoke({"query": state.get("query", "")})
    label = (resp.content or "").strip().lower()
    logger.info(f"Intent classification result: {label}")
    if label not in {"today_summary", "recent_summary", "cross_days_trend", "general_qa"}:
        label = _classify_intent(state.get("query", ""))
    return {"intent": label}


def _parse_time_range(intent: str) -> Tuple[Optional[str], Optional[str]]:
    """解析意图并返回初始时间范围"""
    today = date.today()
    if intent == "today_summary":
        d = today.strftime("%Y-%m-%d")
        return d, d
    if intent == "recent_summary":
        return (today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    if intent == "cross_days_trend":
        return (today - timedelta(days=30)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    return None, None


def _get_retrieval_config(intent: str) -> Dict[str, Any]:
    """获取检索配置"""
    if intent == "today_summary":
        return {
            "min_results_for_llm_check": 1,  # 至少有1条才让LLM判断
            "time_expansion_steps": [1, 7, 14, 30],
            "max_attempts": 3,  # 最多尝试3次扩展
            "max_time_range": 30,
        }
    elif intent == "recent_summary":
        return {
            "min_results_for_llm_check": 2,
            "time_expansion_steps": [7, 14, 30, 60],
            "max_attempts": 3,
            "max_time_range": 60,
        }
    elif intent == "cross_days_trend":
        return {
            "min_results_for_llm_check": 3,
            "time_expansion_steps": [15, 30, 60, 90],
            "max_attempts": 3,
            "max_time_range": 90,
        }
    else:  # general_qa
        return {
            "min_results_for_llm_check": 1,
            "time_expansion_steps": [7, 30, 90, 180, 365],
            "max_attempts": 4,
            "max_time_range": 365,
        }


async def time_range_node(state: AgentState) -> dict:
    """确定初始时间范围"""
    start_date, end_date = _parse_time_range(state.get("intent", ""))
    return {
        "start_date": start_date,
        "end_date": end_date,
        "original_start_date": start_date,
        "original_end_date": end_date
    }


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
    
    logger.info(f"预过滤获取到 {len(rows)} 条候选记录")
    
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
    result = {
        "answer": data.get("answer", "无法回答"),
        "evidence": data.get("evidence", []),
        "trend_analysis": data.get("trend_analysis", []),
        "insights": data.get("insights", []),
        "sources": data.get("sources", []),
        "confidence": data.get("confidence", "中")
    }
    
    if not isinstance(result["evidence"], list):
        result["evidence"] = [str(result["evidence"])]
    if not isinstance(result["trend_analysis"], list):
        result["trend_analysis"] = [str(result["trend_analysis"])]
    if not isinstance(result["insights"], list):
        result["insights"] = [str(result["insights"])]
    if not isinstance(result["sources"], list):
        result["sources"] = []
    
    if result["confidence"] not in ["高", "中", "低"]:
        result["confidence"] = "中"
    
    return result


def _parse_json_response(raw_response: str) -> Dict[str, Any]:
    """解析LLM返回的JSON响应"""
    content = raw_response.strip()
    
    if "```json" in content:
        try:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                json_str = content[start:end].strip()
                return _validate_and_fix_response(json.loads(json_str))
        except (json.JSONDecodeError, ValueError):
            pass

    elif content.startswith("```") and content.endswith("```"):
        try:
            json_str = content[3:-3].strip()
            return _validate_and_fix_response(json.loads(json_str))
        except (json.JSONDecodeError, ValueError):
            pass

    try:
        return _validate_and_fix_response(json.loads(content))
    except (json.JSONDecodeError, ValueError):
        pass

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

async def llm_check_relevance(query: str, records: List[Dict]) -> Dict[str, Any]:
    """使用LLM判断检索结果是否相关"""
    if not records:
        return {
            "can_answer": False,
            "confidence": "低",
            "reason": "没有检索到任何记录",
            "missing_info": "需要相关的日记记录"
        }
    
    # 构建记录摘要（避免token过多）
    records_summary = "\n".join([
        f"[{r.get('record_date')}] {r.get('content', '')[:200]}..."
        for r in records[:5]  # 只取前5条
    ])
    
    llm = get_llm()
    prompt = build_relevance_check_prompt()
    chain = prompt | llm
    
    try:
        resp = await chain.ainvoke({
            "query": query,
            "records_summary": records_summary
        })
        
        content = resp.content.strip()
        
        # 解析JSON
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                json_str = content[start:end].strip()
                result = json.loads(json_str)
                return result
        
        result = json.loads(content)
        return result
        
    except Exception as e:
        logger.error(f"LLM相关性判断失败: {e}")
        # 失败时保守返回，认为可以尝试回答
        return {
            "can_answer": True,
            "confidence": "中",
            "reason": "LLM判断失败，保守返回",
            "missing_info": ""
        }


async def rerank_and_fetch(
    session: AsyncSession,
    vector_results: List[Dict],
    fts_results: List[Dict],
    top_k: int,
) -> List[Dict]:
    """使用RRF重排序并获取记录"""
    k = 60
    ranked_list: Dict[int, float] = {}
    
    for i, doc in enumerate(vector_results):
        doc_id = doc["id"]
        if doc_id not in ranked_list:
            ranked_list[doc_id] = 0.0
        ranked_list[doc_id] += 1 / (k + i)

    for i, doc in enumerate(fts_results):
        doc_id = doc["id"]
        if doc_id not in ranked_list:
            ranked_list[doc_id] = 0.0
        ranked_list[doc_id] += 1 / (k + i)

    sorted_docs = sorted(ranked_list.items(), key=lambda x: x[1], reverse=True)
    top_ids = [doc_id for doc_id, score in sorted_docs[:top_k]]

    if not top_ids:
        return []

    sql = text("""
        SELECT id, user_id, record_date, content, mood_score, reflections
        FROM daily_records
        WHERE id = ANY(:ids)
    """)
    
    result = await session.execute(sql, {"ids": top_ids})
    rows = result.fetchall()
    row_map = {row.id: row for row in rows}
    ordered_rows = [row_map[doc_id] for doc_id in top_ids if doc_id in row_map]

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "record_date": r.record_date,
            "content": r.content,
            "mood_score": r.mood_score,
            "reflections": r.reflections,
        }
        for r in ordered_rows
    ]


async def _search_in_time_range(
    session: AsyncSession,
    qv: List[float],
    query: str,
    user_id: int,
    start_date: Optional[str],
    end_date: Optional[str],
    top_k: int = 10
) -> List[Dict]:
    """在指定时间范围内执行混合搜索"""
    vector_str = "[" + ",".join(map(str, qv)) + "]"
    
    # 向量搜索
    vs_filters = ["user_id = :user_id", "vector IS NOT NULL"]
    if start_date:
        vs_filters.append("record_date >= :start_date")
    if end_date:
        vs_filters.append("record_date <= :end_date")
    vs_where_sql = " AND ".join(vs_filters)

    # FTS搜索
    fts_filters = ["user_id = :user_id"]
    if start_date:
        fts_filters.append("record_date >= :start_date")
    if end_date:
        fts_filters.append("record_date <= :end_date")
    fts_where_sql = " AND ".join(fts_filters)

    base_params = {"user_id": user_id, "top_k": top_k}
    if start_date:
        base_params["start_date"] = start_date
    if end_date:
        base_params["end_date"] = end_date

    vector_sql = f"""
        SELECT id, (1 - (vector <=> (:qv)::vector)) AS similarity
        FROM daily_records
        WHERE {vs_where_sql}
        ORDER BY vector <=> (:qv)::vector
        LIMIT :top_k
    """
    vector_params = {"qv": vector_str, **base_params}

    # 处理FTS查询
    query_words = (query or "").split()
    if not query_words:
        fts_rows = []
        try:
            vector_result = await session.execute(text(vector_sql), vector_params)
            vector_rows = [{"id": r.id, "score": r.similarity} for r in vector_result.fetchall()]
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            vector_rows = []
        return await rerank_and_fetch(session, vector_rows, fts_rows, top_k)
    
    fts_query_str = " | ".join(query_words)
    fts_sql = f"""
        SELECT id, ts_rank_cd(to_tsvector('simple', content || ' ' || reflections), to_tsquery('simple', :query)) as rank
        FROM daily_records
        WHERE to_tsvector('simple', content || ' ' || reflections) @@ to_tsquery('simple', :query)
        AND {fts_where_sql}
        ORDER BY rank DESC
        LIMIT :top_k
    """
    fts_params = {"query": fts_query_str, **base_params}

    try:
        vector_result, fts_result = await asyncio.gather(
            session.execute(text(vector_sql), vector_params),
            session.execute(text(fts_sql), fts_params),
            return_exceptions=True
        )
        
        vector_rows = []
        fts_rows = []
        
        if not isinstance(vector_result, Exception):
            vector_rows = [{"id": r.id, "score": r.similarity} for r in vector_result.fetchall()]
        else:
            logger.error(f"向量搜索失败: {vector_result}")
        
        if not isinstance(fts_result, Exception):
            fts_rows = [{"id": r.id, "score": r.rank} for r in fts_result.fetchall()]
        else:
            logger.error(f"FTS搜索失败: {fts_result}")
        
        return await rerank_and_fetch(session, vector_rows, fts_rows, top_k)
        
    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        return []


async def retrieve_node(state: dict, session: AsyncSession) -> dict:
    """
    混合检索策略：规则过滤 + LLM判断
    
    流程：
    1. 快速规则检查：如果结果数 < 最小阈值，直接扩展（不浪费LLM调用）
    2. LLM相关性判断：如果结果数 >= 阈值，让LLM判断是否相关
    3. 动态扩展：如果LLM认为不相关，扩大时间范围重试
    4. 上限保护：最多尝试N次，避免无限循环
    """
    qv = state.get("query_vector")
    query = state.get("query")
    user_id = state["user_id"]
    intent = state.get("intent", "general_qa")
    
    if not qv or not query:
        retrieved = state.get("candidates", [])
        logger.info(f"无向量或查询，使用候选集，数量: {len(retrieved)}")
        return {"retrieved": retrieved}

    # 获取配置
    config = _get_retrieval_config(intent)
    min_results_for_llm = config["min_results_for_llm_check"]
    expansion_steps = config["time_expansion_steps"]
    max_attempts = config["max_attempts"]
    max_time_range = config["max_time_range"]
    
    original_start = state.get("original_start_date")
    original_end = state.get("original_end_date")
    current_start = original_start
    current_end = original_end
    
    search_logs = []
    attempts = 0
    
    # 迭代检索 + LLM判断
    while attempts < max_attempts:
        attempts += 1
        logger.info(f"=== 尝试 {attempts}/{max_attempts} ===")
        logger.info(f"时间范围: {current_start} ~ {current_end}")
        
        # 执行检索
        retrieved = await _search_in_time_range(
            session, qv, query, user_id, current_start, current_end
        )
        
        log_entry = {
            "attempt": attempts,
            "start_date": current_start,
            "end_date": current_end,
            "results_count": len(retrieved)
        }
        
        logger.info(f"检索到 {len(retrieved)} 条记录")
        
        # === 规则快速过滤 ===
        if len(retrieved) < min_results_for_llm:
            logger.info(f"结果数 < {min_results_for_llm}，直接扩展时间范围")
            log_entry["decision"] = "too_few_results"
            log_entry["llm_used"] = False
            search_logs.append(log_entry)
            
            # 扩展时间范围
            if attempts >= len(expansion_steps):
                logger.warning("已达最大尝试次数")
                break
            
            if not original_start:
                break
            
            extra_days = expansion_steps[attempts - 1]
            new_start_date = date.fromisoformat(original_start) - timedelta(days=extra_days)
            current_start = new_start_date.strftime("%Y-%m-%d")
            
            # 检查是否超过最大范围
            if (date.today() - new_start_date).days > max_time_range:
                logger.info("达到最大时间范围")
                break
            
            continue
        
        # === LLM判断相关性 ===
        logger.info("结果数足够，调用LLM判断相关性")
        relevance = await llm_check_relevance(query, retrieved)
        
        log_entry["llm_used"] = True
        log_entry["llm_decision"] = relevance
        search_logs.append(log_entry)
        
        logger.info(f"LLM判断: can_answer={relevance.get('can_answer')}, "
                   f"confidence={relevance.get('confidence')}, "
                   f"reason={relevance.get('reason')}")
        
        # 如果LLM认为可以回答，返回结果
        if relevance.get("can_answer"):
            return {
                "retrieved": retrieved,
                "search_expanded": current_start != original_start,
                "expanded_start_date": current_start if current_start != original_start else None,
                "original_start_date": original_start,
                "search_logs": search_logs,
                "llm_confidence": relevance.get("confidence", "中"),
                "llm_reason": relevance.get("reason", "")
            }
        
        # LLM认为不能回答，扩展时间范围
        logger.info("LLM认为结果不相关，扩展时间范围")
        
        if attempts >= len(expansion_steps):
            logger.warning("已达最大尝试次数，返回当前结果")
            break
        
        if not original_start:
            break
        
        extra_days = expansion_steps[attempts - 1]
        new_start_date = date.fromisoformat(original_start) - timedelta(days=extra_days)
        current_start = new_start_date.strftime("%Y-%m-%d")
        
        if (date.today() - new_start_date).days > max_time_range:
            logger.info("达到最大时间范围")
            break
    
    # 达到最大尝试次数，返回最后一次结果或兜底
    if len(retrieved) == 0:
        logger.warning("所有尝试都失败，使用时间兜底")
        fallback_sql = """
            SELECT id, user_id, record_date, content, mood_score, reflections
            FROM daily_records
            WHERE user_id = :user_id
            ORDER BY record_date DESC
            LIMIT 5
        """
        result = await session.execute(text(fallback_sql), {"user_id": user_id})
        fallback_rows = result.fetchall()
        
        retrieved = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "record_date": r.record_date,
                "content": r.content,
                "mood_score": r.mood_score,
                "reflections": r.reflections,
            }
            for r in fallback_rows
        ]
        
        search_logs.append({"decision": "fallback", "results_count": len(retrieved)})
    
    return {
        "retrieved": retrieved,
        "search_expanded": True,
        "expanded_start_date": current_start,
        "original_start_date": original_start,
        "search_logs": search_logs,
        "max_attempts_reached": True
    }


def _add_retrieval_context(data: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
    """为响应添加检索上下文说明"""
    notes = []
    
    # LLM置信度说明
    if state.get("llm_confidence"):
        confidence = state.get("llm_confidence")
        if confidence == "低":
            notes.append("检索结果的相关性置信度较低")
    
    # 时间扩展说明
    if state.get("search_expanded"):
        original_start = state.get("original_start_date")
        expanded_start = state.get("expanded_start_date")
        original_end = state.get("original_end_date")
        if original_start and expanded_start:
            notes.append(
                f"查询范围已从 {original_start}~{original_end} 扩展至 {expanded_start}~{original_end}"
            )
    
    # 最大尝试说明
    if state.get("max_attempts_reached"):
        notes.append("已尝试多次扩展检索范围")
    
    if notes:
        context_note = "\n\n注：" + "；".join(notes) + "。"
        if "answer" in data:
            data["answer"] = data["answer"] + context_note
    
    return data


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
    
    parsed_data = _parse_json_response(resp.content)
    parsed_data = _add_retrieval_context(parsed_data, state)
    
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
    
    parsed_data = _parse_json_response(resp.content)
    parsed_data = _add_retrieval_context(parsed_data, state)
    
    return {
        "result": {
            "used_rag": True,
            "data": parsed_data
        }
    }