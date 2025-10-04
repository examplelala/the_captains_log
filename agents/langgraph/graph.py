
from typing import Any, Dict
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession
from agents.langgraph.state import AgentState
from agents.langgraph.nodes import (
    classify_intent_node,
    time_range_node,
    prefilter_node,
    need_rag,
    embed_node,
    retrieve_node,
    generate_no_rag_node,
    generate_with_history_node,
)
from functools import partial

def build_graph(session: AsyncSession):
    g = StateGraph(AgentState)

    # 核心节点
    g.add_node("classify", classify_intent_node)
    g.add_node("time_range", time_range_node)
    g.add_node("prefilter", partial(prefilter_node, session=session))
    g.add_node("retrieve", partial(retrieve_node, session=session))
    g.add_node("embed", embed_node)
    g.add_node("generate_no_rag", generate_no_rag_node)
    g.add_node("generate_with_history", generate_with_history_node)

    # 主干流转
    g.set_entry_point("classify")
    g.add_edge("classify", "time_range")
    g.add_edge("time_range", "prefilter")

    # 分支：是否需要检索
    def branch_decider(state: AgentState) -> str:
        return "rag" if need_rag(state) else "no_rag"

    g.add_conditional_edges(
        "prefilter",
        branch_decider,
        {
            "no_rag": "generate_no_rag",
            "rag": "embed",
        },
    )

    g.add_edge("embed", "retrieve")
    g.add_edge("retrieve", "generate_with_history")
    g.add_edge("generate_no_rag", END)
    g.add_edge("generate_with_history", END)

    return g.compile()


async def respond(user_id: int, user_query: str,session: AsyncSession) -> Dict[str, Any]:
    app = build_graph(session)
    initial: AgentState = {"user_id": user_id, "query": user_query}
    final_state: AgentState = await app.ainvoke(initial)
    return final_state.get("result", {})


