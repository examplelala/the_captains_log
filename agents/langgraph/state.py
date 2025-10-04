from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    user_id: int
    query: str
    intent: str
    start_date: Optional[str]
    end_date: Optional[str]
    candidates: List[Dict[str, Any]]
    query_vector: Optional[List[float]]
    retrieved: List[Dict[str, Any]]
    result: Dict[str, Any]


