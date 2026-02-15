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
    pages: List[dict]  # [{page_num, content, sections}, ...]
    
    # MÉTADONNÉES pour traçabilité
    total_pages: int
    extraction_time: float
    llama_parse_job_id: Optional[str]