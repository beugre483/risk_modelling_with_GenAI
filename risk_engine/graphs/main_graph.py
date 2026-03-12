# graphs/main_graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..core.state import MainState
from ..nodes.extraction import upload_document_node, extract_document_node
from ..nodes.contextualise import summarize_page_node, should_continue_summary
from ..nodes.aloe import extract_aloe_objects_node, should_continue_aloe_extraction
from ..nodes.risk_identification import analyze_risks_page_node, should_continue_risk_analysis
from ..nodes.aloe_links import extract_aloe_links_node, should_continue_aloe_links
from ..nodes.aloe_vulnerabilities import extract_aloe_vulnerabilities_node, should_continue_aloe_vulnerabilities


def create_main_graph():
    graph = StateGraph(MainState)

    # Nœuds
    graph.add_node("upload", upload_document_node)
    graph.add_node("extract", extract_document_node)
    graph.add_node("summarize_page", summarize_page_node)
    graph.add_node("extract_aloe", extract_aloe_objects_node)
    graph.add_node("extract_aloe_links", extract_aloe_links_node)
    graph.add_node("extract_aloe_vulnerabilities", extract_aloe_vulnerabilities_node)
    graph.add_node("analyze_risk_page", analyze_risks_page_node)

    # Flow
    graph.set_entry_point("upload")
    graph.add_edge("upload", "extract")
    graph.add_edge("extract", "summarize_page")

    graph.add_conditional_edges(
        "summarize_page",
        should_continue_summary,
        {"continue": "summarize_page", "finish": "extract_aloe"}
    )

    # ✅ Une seule fois, vers extract_aloe_links
    graph.add_conditional_edges(
        "extract_aloe",
        should_continue_aloe_extraction,
        {"continue": "extract_aloe", "finish": "extract_aloe_links"}
    )

    graph.add_conditional_edges(
        "extract_aloe_links",
        should_continue_aloe_links,
        {"continue": "extract_aloe_links", "finish": "extract_aloe_vulnerabilities"}
    )

    graph.add_conditional_edges(
        "extract_aloe_vulnerabilities",
        should_continue_aloe_vulnerabilities,
        {"continue": "extract_aloe_vulnerabilities", "finish": "analyze_risk_page"}
    )

    graph.add_conditional_edges(
        "analyze_risk_page",
        should_continue_risk_analysis,
        {"continue": "analyze_risk_page", "finish": END}
    )

    return graph.compile(checkpointer=MemorySaver())