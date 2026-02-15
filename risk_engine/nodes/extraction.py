# src/risk_engine/nodes/extraction.py

from ..core.state import MainState
from ..services.llama_parse_services import get_llama_parse_service
from typing import Dict
import os


def upload_document_node(state: MainState) -> Dict:
    """
    Nœud : vérifie que le fichier uploadé existe
    """
    file_path = state["uploaded_file_path"]
    
    if not os.path.exists(file_path):
        return {
            **state,
            "upload_status": "failed",
            "error_message": f"Fichier introuvable: {file_path}"
        }
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
    print(f" Fichier trouvé: {state['file_name']} ({file_size:.2f} MB)")
    
    return {
        **state,
        "upload_status": "completed"
    }


def extract_document_node(state: MainState) -> Dict:
    """
    Nœud principal : extraction avec LlamaParse
    """
    print(f" Extraction en cours: {state['file_name']}")
    
    try:
        # 1. Récupère le service LlamaParse
        llama_service = get_llama_parse_service()
        
        # 2. Lance l'extraction
        result = llama_service.extract_document(state["uploaded_file_path"])
        
        # 3. Met à jour le state
        print(f" Extraction terminée: {result['total_pages']} pages en {result['extraction_time']:.2f}s")
        
        return {
            **state,
            "extraction_status": "completed",
            "pages": result["pages"],
            "total_pages": result["total_pages"],
            "raw_text": result["raw_text"],
            "extraction_time": result["extraction_time"]
        }
    
    except Exception as e:
        print(f" Erreur d'extraction: {e}")
        return {
            **state,
            "extraction_status": "failed",
            "error_message": str(e)
        }