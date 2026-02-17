from typing import TypedDict, List, Optional, Dict



class MainState(TypedDict):
    # INPUT (fourni par l'utilisateur via Streamlit)
    uploaded_file_path: str
    file_name: str
    file_type: str  # "pdf", "docx", etc.
    
    # PROGRESSION
    upload_status: str  # "pending", "completed", "failed"
    extraction_status: str  # "pending", "in_progress", "completed", "failed"
    
    # OUTPUT STRUCTURÉ (résultat de LlamaParse)
    pages: List[dict]  # [{page_num, content}, ...]
    total_pages: int
    # MÉTADONNÉES pour traçabilité
    total_pages: int
    extraction_time: float
    llama_parse_job_id: Optional[str]
    edit_mode: Optional[str]  # "human" | "llm" | None
    edited_pages: List[int]  # [1, 3, 5] - pages modifiées
    edit_history: List[Dict]  # Historique des modifications
    target_page_num: Optional[int]  
    edit_instruction: Optional[str] 