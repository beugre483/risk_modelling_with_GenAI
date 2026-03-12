import streamlit as st
import markdown

def display_pages_as_word(pages, total_pages):
    """
    Affiche les pages extraites dans un style Word avec défilement
    
    Args:
        pages: Liste des pages
        total_pages: Nombre total de pages
    """
    
    # CSS pour les pages Word
    st.markdown("""
    <style>
    .page-viewer-container {
        background-color: #2a2a2a;
        padding: 30px;
        border-radius: 12px;
        max-height: 80vh;
        overflow-y: auto;
        margin: 20px 0;
    }
    
    .word-page {
        background-color: #ffffff;
        color: #000000;
        padding: 2.54cm 3cm;
        margin: 30px auto;
        width: 21cm;
        min-height: 29.7cm;
        box-shadow: 0 5px 25px rgba(0,0,0,0.4);
        border-radius: 2px;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        position: relative;
        page-break-after: always;
    }
    
    .page-number {
        position: absolute;
        bottom: 1.5cm;
        right: 2cm;
        color: #666;
        font-size: 10pt;
        font-family: 'Arial', sans-serif;
    }
    
    .word-page h1 {
        color: #000000 !important;
        font-size: 18pt !important;
        font-weight: bold !important;
        margin-top: 0 !important;
        margin-bottom: 12pt !important;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .word-page h2 {
        color: #000000 !important;
        font-size: 14pt !important;
        font-weight: bold !important;
        margin-top: 10pt !important;
        margin-bottom: 6pt !important;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .word-page h3 {
        color: #000000 !important;
        font-size: 12pt !important;
        font-weight: bold !important;
        margin-top: 8pt !important;
        margin-bottom: 4pt !important;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .word-page p {
        margin-bottom: 8pt !important;
        text-align: justify !important;
        color: #000000 !important;
    }
    
    .word-page ul, .word-page ol {
        margin-left: 1.5cm !important;
        margin-bottom: 8pt !important;
    }
    
    .word-page li {
        margin-bottom: 4pt !important;
        color: #000000 !important;
    }
    
    /* Scrollbar personnalisée */
    .page-viewer-container::-webkit-scrollbar {
        width: 12px;
    }
    
    .page-viewer-container::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 6px;
    }
    
    .page-viewer-container::-webkit-scrollbar-thumb {
        background: #4a4a4a;
        border-radius: 6px;
    }
    
    .page-viewer-container::-webkit-scrollbar-thumb:hover {
        background: #6366F1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Génère le HTML pour toutes les pages
    pages_html = '<div class="page-viewer-container">\n'
    
    for page in pages:
        # 1. On utilise bien page et on remet les extensions !
        content_html = markdown.markdown(
            page['content'],
            extensions=['extra','nl2br']
        )
        
        # 2. ZÉRO espace au début des lignes ET on utilise bien page
        pages_html += f"""<div class="word-page">
{content_html}
</div>
"""
    
    pages_html += '</div>'
    
    st.markdown(pages_html, unsafe_allow_html=True)