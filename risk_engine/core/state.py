# core/state.py

from typing import TypedDict, List, Optional, Dict


class MainState(TypedDict):
    # INPUT
    uploaded_file_path: str
    file_name: str
    file_type: str
    
    # PROGRESSION
    upload_status: str
    extraction_status: str
    
    # OUTPUT EXTRACTION
    pages: List[Dict]  # [{"page_num": 1, "content": "..."}, ...]
    total_pages: int
    raw_text: str
    extraction_time: float
    llama_parse_job_id: Optional[str]
    
    # ÉDITION
    edit_mode: Optional[str]  # "human" | "llm" | "skip"
    target_page_num: Optional[int]
    edit_instruction: Optional[str]
    edited_pages: List[int]
    edit_history: List[Dict]
    
    # RÉSUMÉ (nouveau)
    current_page_index: int  # Pour la boucle de résumé
    page_summaries: List[Dict]  # [{"page_num": 1, "summary": "..."}, ...]
    global_summary: str 

    # ERREURS
    error_message: Optional[str]
    
    current_risk_page_index: int  
    page_risks: List[Dict]  # Risques par page
    all_identified_elements: List[str] 
    all_identified_threats: List[str]  