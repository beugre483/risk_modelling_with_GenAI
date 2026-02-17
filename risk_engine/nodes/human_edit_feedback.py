# nodes/human_feedback.py

from langgraph.types import interrupt
from ..core.state import MainState
from typing import Dict


def edit_decision_node(state: MainState) -> Dict:
    """
    Demande à l'utilisateur s'il veut modifier le document
    """
    user_choice = interrupt({
        "question": "Veux-tu modifier le document ?",
        "options": ["human", "llm", "skip"],
        "total_pages": state["total_pages"]
    })
    
    return {
        **state,
        "edit_mode": user_choice  # "human" | "llm" | "skip"
    }


def human_edit_node(state: MainState) -> Dict:
    """
    Pause pour que l'humain édite les pages via l'interface
    """
    edited_data = interrupt(state["pages"])
    
    # Streamlit retournera:
    # {
    #   "pages": [...pages modifiées...],
    #   "edited_pages": [2, 5]
    # }
    
    return {
        **state,
        "pages": edited_data["pages"],
        "edited_pages": edited_data.get("edited_pages", []),
        "edit_history": state.get("edit_history", []) + [{
            "type": "human_edit",
            "edited_pages": edited_data.get("edited_pages", [])
        }]
    }


def llm_edit_instruction_node(state: MainState) -> Dict:
    """
    Pause pour que l'utilisateur donne une instruction au LLM
    """
    instruction = interrupt("Quelle modification Voulez-vous  que l'IA fasse sur les documents générés ?")
    
    # Streamlit retournera:
    # {
    #   "page_num": 3,
    # }
    
    return {
        **state,
        "target_page_num": instruction["page_num"],
        "edit_instruction": instruction["instruction"]
    }