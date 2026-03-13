# graphs/main_graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..core.state import MainState
from ..nodes.extraction import upload_document_node, extract_document_node
from ..nodes.contextualise import summarize_page_node, should_continue_summary
from ..nodes.risk_identification import analyze_risks_page_node, should_continue_risk_analysis


def create_main_graph():
    graph = StateGraph(MainState)

    # Extraction
    graph.add_node("upload", upload_document_node)
    graph.add_node("extract", extract_document_node)

    # Résumé
    graph.add_node("summarize_page", summarize_page_node)

    # Risques
    graph.add_node("analyze_risk_page", analyze_risks_page_node)

    graph.set_entry_point("upload")
    graph.add_edge("upload", "extract")
    graph.add_edge("extract", "summarize_page")

    graph.add_conditional_edges(
        "summarize_page",
        should_continue_summary,
        {
            "continue": "summarize_page",
            "finish": "analyze_risk_page"
        }
    )

    graph.add_conditional_edges(
        "analyze_risk_page",
        should_continue_risk_analysis,
        {
            "continue": "analyze_risk_page",
            "finish": END
        }
    )

    return graph.compile(checkpointer=MemorySaver())