# src/risk_engine/graphs/main_graph.py

from langgraph.graph import StateGraph, END
from ..core.state import MainState
from ..nodes.extraction import upload_document_node, extract_document_node


def create_main_graph():
    """
    Graphe principal - Version initiale avec extraction uniquement
    """
    graph = StateGraph(MainState)
    
    #  NŒUDS D'EXTRACTION 
    graph.add_node("upload", upload_document_node)
    graph.add_node("extract", extract_document_node)
    
    #  FLOW SIMPLE
    graph.set_entry_point("upload")
    graph.add_edge("upload", "extract")
    graph.add_edge("extract", END)
    
    return graph.compile()