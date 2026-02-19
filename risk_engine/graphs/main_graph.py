# graphs/main_graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..core.state import MainState
from ..nodes.extraction import upload_document_node, extract_document_node
from ..nodes.human_edit_feedback import (
    edit_decision_node,
    human_edit_node,
    llm_edit_instruction_node
)
from ..nodes.llm_editor import llm_edit_node
from ..nodes.contextualise import summarize_page_node, should_continue_summary
from ..nodes.risk_identification import analyze_risks_page_node, should_continue_risk_analysis


def create_main_graph():
    """
    Graphe principal avec toutes les étapes du pipeline
    """
    graph = StateGraph(MainState)
    
    # Extraction
    graph.add_node("upload", upload_document_node)
    graph.add_node("extract", extract_document_node)
    
    # Édition
    graph.add_node("edit_decision", edit_decision_node)
    graph.add_node("human_edit", human_edit_node)
    graph.add_node("llm_instruction", llm_edit_instruction_node)
    graph.add_node("llm_edit", llm_edit_node)
    
    # Résumé
    graph.add_node("summarize_page", summarize_page_node)
    
    graph.add_node("analyze_risk_page", analyze_risks_page_node)
    
    graph.set_entry_point("upload")
    graph.add_edge("upload", "extract")
    graph.add_edge("extract", "edit_decision")
    
    graph.add_conditional_edges(
        "edit_decision",
        lambda state: state.get("edit_mode", "skip"),
        {
            "human": "human_edit",
            "llm": "llm_instruction",
            "skip": "summarize_page"
        }
    )
    
    graph.add_edge("human_edit", "summarize_page")
    
    graph.add_edge("llm_instruction", "llm_edit")
    graph.add_edge("llm_edit", "summarize_page")
    
    graph.add_conditional_edges(
        "summarize_page",
        should_continue_summary,
        {
            "continue": "summarize_page",  # Boucle
            "finish": "analyze_risk_page"
        }
    )
    
    graph.add_conditional_edges(
        "analyze_risk_page",
        should_continue_risk_analysis,
        {
            "continue": "analyze_risk_page",  # Boucle
            "finish": END
        }
    )
    
    return graph.compile(checkpointer=MemorySaver())
