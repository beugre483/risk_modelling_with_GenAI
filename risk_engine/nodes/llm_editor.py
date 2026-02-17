# nodes/llm_editor.py

from ..core.state import MainState
from ..services.llm_client import get_llm
from typing import Dict
import re
import time


def llm_edit_node(state: MainState) -> Dict:
    """
    Le LLM modifie la page spécifiée selon l'instruction
    """
    target_page_num = state["target_page_num"]
    instruction = state["edit_instruction"]
    
    # Trouve la page à modifier
    target_page = None
    for page in state["pages"]:
        if page["page_num"] == target_page_num:
            target_page = page
            break
    
    if not target_page:
        return {
            **state,
            "error_message": f"Page {target_page_num} introuvable"
        }
    
    # Appelle le LLM
    llm = get_llm()
    
    prompt = f"""Tu es un assistant d'édition de documents.

INSTRUCTION:
{instruction}

PAGE {target_page_num} - CONTENU ACTUEL:
{target_page["content"]}

TÂCHE:
- Applique la modification demandée
- Retourne UNIQUEMENT le nouveau contenu complet de la page
- Préserve le format markdown
- Ne rajoute PAS de commentaires ou explications

NOUVEAU CONTENU:"""
    
    new_content = llm.invoke(prompt)
    
    # Nettoie la réponse (enlève backticks si présents)
    new_content = _clean_llm_response(new_content)
    
    # Met à jour la page
    target_page["content"] = new_content
    
    return {
        **state,
        "edited_pages": list(set(state.get("edited_pages", []) + [target_page_num])),
        "edit_history": state.get("edit_history", []) + [{
            "type": "llm_edit",
            "timestamp": time.time(),
            "instruction": instruction,
            "page_num": target_page_num
        }],
        "error_message": None
    }


def _clean_llm_response(response: str) -> str:
    """Nettoie la réponse du LLM"""
    # Enlève ```markdown ou ``` au début/fin
    response = re.sub(r'^```markdown\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'^```\s*', '', response)
    response = re.sub(r'\s*```$', '', response)
    return response.strip()