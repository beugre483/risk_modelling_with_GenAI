# src/risk_engine/services/llama_parse_client.py

import os
import re
import nest_asyncio
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from typing import List, Dict
import time

load_dotenv()
nest_asyncio.apply()


class LlamaParseService:
    """Service d'extraction de contenu avec LlamaParse"""
    
    def __init__(self, api_key_env='LLAMA_CLOUD_API_KEY'):
        load_dotenv()
        
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f" {api_key_env} not found in environment variables.")
        
        # TON PROMPT COMPLET (inchangé)
        self.parsing_instruction = """
You are a document parser specialized in extracting key information from project management documents. Extract the information exactly as it appears, without any rephrasing or interpretation.
Do not rephrase, summarize, or interpret any content. Write and extract the information exactly as it appears in the document, word for word, including all formatting, bullet points, and line breaks.

Preserve the original section titles and the hierarchical structure (headings, subheadings, etc.) as they appear in the document. Reflect the document's outline and nesting of sections in your output, so that the parent-child relationships between sections and subsections are clear.

**Output instructions:**
- Output the extracted content in markdown format, not JSON.
- For each main section, use a level 1 markdown heading (`#`) and write the title in ALL UPPERCASE.
- For each subsection, use a level 2 markdown heading (`##`) and write the title in Capitalized or lowercase as appropriate.
- Place the content directly below its title.
- Preserve the original hierarchy and order of sections and subsections as in the document.
- If you encounter a table, figure, or graph, do not simply extract it as-is. Instead, describe the information contained in the table, figure, or graph using full sentences and paragraphs, in the language of the document. Translate all visual elements into textual explanations, ensuring that the meaning, relationships, and data are fully conveyed. Avoid losing any detail, and integrate the content into the narrative as if you were explaining it to someone who cannot see the visual elements.
IMPORTANT:- For each page in the document, wrap its entire content (including all headings, text, and formatting) inside a tag of the form <pageN> ... </pageN>, where N is the page number (e.g., <page1> ... </page1>, <page2> ... </page2>, etc.).
- Place all extracted markdown content for each page inside its corresponding tag, and increment the page number for each new page.
- Do not merge content from different pages into the same tag.

**Example:**

<page1>
# PROJECT OBJECTIVES
The project aims to improve digital infrastructure...

## Key performance indicators
- Increase internet penetration by 20%
- Reduce costs by 15%

# ORGANIZATION AND GOVERNANCE
The project is managed by...

## Steering committee
The steering committee includes...

## Figure 1: Internet Penetration Growth
The graph shows a steady increase in internet penetration from 2015 to 2020, with a peak growth rate of 25% in 2018. The x-axis represents years, and the y-axis represents the percentage of internet penetration.

(Continue in this format for all sections and subsections.)
</page1>

"""
        
        # Initialisation de LlamaParse
        self.parser = LlamaParse(
            result_type='markdown',
            parsing_instruction=self.parsing_instruction,
            api_key=self.api_key,
            verbose=True
        )
        
        self.file_extractor = {
            ".pdf": self.parser,
            ".docx": self.parser,
            ".txt": self.parser
        }
    
    def extract_content_from_file(self, file_path: str) -> str:
        """
        Extrait le contenu brut d'un fichier avec LlamaParse.
        Retourne le texte complet avec balises <pageN>
        """
        try:
            documents = SimpleDirectoryReader(
                input_files=[file_path],
                file_extractor=self.file_extractor
            ).load_data()
            
            return '\n'.join([doc.text for doc in documents]) if documents else ""
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction: {e}")
    
    def parse_pages_from_text(self, text: str) -> List[Dict]:
        """
        Découpe le texte brut en pages avec algorithme Regex.
        
        Returns:
            [
                {'page_num': 1, 'content': '...'},
                {'page_num': 2, 'content': '...'},
                ...
            ]
        """
        if not text:
            return []
        
        # 1. Découpe par balises </pageN>
        parts = re.split(r'</\s*page\s*\d+\s*>', text, flags=re.IGNORECASE)
        
        pages_data = []
        page_counter = 1
        
        for part in parts:
            # 2. Nettoie les balises <pageN>
            clean_content = re.sub(
                r'<\s*page\s*\d+\s*>', 
                '', 
                part, 
                flags=re.IGNORECASE
            ).strip()
            
            if clean_content:
                pages_data.append({
                    "page_num": page_counter,
                    "content": clean_content
                })
                page_counter += 1
        
        return pages_data
    
    def extract_document(self, file_path: str) -> Dict:
        """
        Méthode principale : extraction complète du document
        
        Returns:
            {
                "pages": [...],
                "total_pages": int,
                "extraction_time": float,
                "raw_text": str
            }
        """
        start_time = time.time()
        
        # 1. Extraction brute avec LlamaParse
        raw_text = self.extract_content_from_file(file_path)
        
        # 2. Parsing en pages structurées
        pages = self.parse_pages_from_text(raw_text)
        
        extraction_time = time.time() - start_time
        
        return {
            "pages": pages,
            "total_pages": len(pages),
            "extraction_time": extraction_time,
            "raw_text": raw_text
        }
    
    def save_to_markdown(self, text: str, output_path: str):
        """Sauvegarde le texte brut dans un fichier .md"""
        if text:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f" Markdown saved to {output_path}")


_llama_parse_service = None

def get_llama_parse_service() -> LlamaParseService:
    """Récupère l'instance unique du service"""
    global _llama_parse_service
    if _llama_parse_service is None:
        _llama_parse_service = LlamaParseService()
    return _llama_parse_service