# app.py

import streamlit as st
from pathlib import Path
import sys
import os

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from risk_engine.graphs.main_graph import create_main_graph
from risk_engine.core.state import MainState
from ui.page_viewer import display_pages_as_word

def load_css():
    css_file = Path(__file__).parent / "ui" / "style.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(
    page_title="Analyseur de Risques Projet",
    page_icon="📊",
    layout="wide"
)

# Init session state
if "result" not in st.session_state:
    st.session_state.graph = create_main_graph()
    st.session_state.config = {"configurable": {"thread_id": "session_001"}}
    st.session_state.result = None
    st.session_state.extraction_done = False
    st.session_state.summarization_done = False
    st.session_state.aloe_done = False
    st.session_state.aloe_links_done = False
    st.session_state.aloe_vulnerabilities_done = False
    st.session_state.risks_done = False
    st.session_state.current_page = "accueil"

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("### 🔑 Clés API")
    
    mistral_key = st.text_input("Clé API Mistral", type="password", placeholder="sk-...")
    llama_key = st.text_input("Clé API Llama Cloud", type="password", placeholder="llx-...")
    
    if mistral_key:
        os.environ["MISTRAL_API_KEY"] = mistral_key
        st.success("✅ Mistral OK")
    
    if llama_key:
        os.environ["LLAMA_CLOUD_API_KEY"] = llama_key
        st.success("✅ Llama Cloud OK")
    
    st.markdown("---")
    
    if st.session_state.extraction_done:
        st.markdown("### 📑 Navigation")
        
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.current_page = "accueil"
            st.rerun()
        
        if st.button("📄 Voir pages", use_container_width=True):
            st.session_state.current_page = "voir_pages"
            st.rerun()
        
        if st.session_state.aloe_done:
            if st.button("🎯 Objets ALOE", use_container_width=True):
                st.session_state.current_page = "aloe"
                st.rerun()
        
        if st.session_state.aloe_links_done:
            if st.button("🔗 Liens ALOE", use_container_width=True):
                st.session_state.current_page = "aloe_links"
                st.rerun()
        
        if st.session_state.aloe_vulnerabilities_done:
            if st.button("🛡️ Vulnérabilités ALOE", use_container_width=True):
                st.session_state.current_page = "aloe_vulnerabilities"
                st.rerun()
        
        if st.session_state.risks_done:
            if st.button("⚠️ Risques", use_container_width=True):
                st.session_state.current_page = "risques"
                st.rerun()

st.title("📊 Analyseur de Risques de Projet")
st.markdown("---")

keys_configured = mistral_key and llama_key

if not keys_configured:
    st.warning("⚠️ Configurez vos clés API dans la sidebar")
    st.stop()


# ===== PAGE RISQUES =====
if st.session_state.current_page == "risques" and st.session_state.risks_done:
    result = st.session_state.result
    
    st.subheader("⚠️ Risques identifiés")
    
    if result.get("page_risks"):
        for page_data in result["page_risks"]:
            with st.expander(f"📄 Page {page_data['page_num']}", expanded=True):
                
                if not page_data.get("vulnerable_elements") and not page_data.get("threat_associations"):
                    st.info("Aucun risque identifié sur cette page")
                    continue
                
                st.markdown("### Éléments vulnérables")
                for elem in page_data.get("vulnerable_elements", []):
                    st.markdown(f"**{elem['element']}**")
                    st.caption(f"📝 {elem['justification']}")
                    st.markdown("---")
                
                st.markdown("### Menaces associées")
                for threat in page_data.get("threat_associations", []):
                    st.markdown(f"**Menace :** {threat['threat']}")
                    st.markdown(f"**Élément :** {threat['vulnerable_element']}")
                    st.markdown(f"**Impact :** {threat['potential_impact']}")
                    st.caption(f"📝 {threat['justification']}")
                    st.markdown("---")
    else:
        st.info("Aucune analyse de risques disponible")
    
    if st.button("⬅️ Retour", use_container_width=True):
        st.session_state.current_page = "accueil"
        st.rerun()
    
    st.stop()


# ===== PAGE VULNÉRABILITÉS ALOE =====
if st.session_state.current_page == "aloe_vulnerabilities" and st.session_state.aloe_vulnerabilities_done:
    result = st.session_state.result
    
    st.subheader("🛡️ Vulnérabilités ALOE identifiées")
    
    if result.get("page_aloe_vulnerabilities"):
        for page_data in result["page_aloe_vulnerabilities"]:
            with st.expander(f"📄 Page {page_data['page_num']}", expanded=True):
                vulnerabilities = page_data.get("vulnerabilities", [])
                
                if not vulnerabilities:
                    st.info("Aucune vulnérabilité identifiée sur cette page")
                    continue
                
                for vuln in vulnerabilities:
                    col_left, col_right = st.columns([2, 3])
                    
                    with col_left:
                        st.markdown(f"### 🔴 {vuln.get('aloe_object_name', 'N/A')}")
                        st.markdown(f"**Attribut vulnérable :** `{vuln.get('vulnerable_attribute', 'N/A')}`")
                        st.markdown(f"**Menace :** {vuln.get('threat', 'N/A')}")
                    
                    with col_right:
                        if vuln.get("propagation_path"):
                            st.markdown(f"**Chemin de propagation :**")
                            st.info(f"🔗 {vuln['propagation_path']}")
                        st.caption(f"📝 {vuln.get('justification', '')}")
                    
                    st.markdown("---")
    else:
        st.info("Aucune analyse de vulnérabilités ALOE disponible")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.current_page = "aloe_links"
            st.rerun()
    with col2:
        if not st.session_state.risks_done:
            if st.button("➡️ Analyser les risques", type="primary", use_container_width=True):
                with st.spinner("🔄 Analyse des risques en cours..."):
                    result = st.session_state.graph.invoke(None, st.session_state.config)
                    st.session_state.result = result
                    st.session_state.risks_done = True
                    st.session_state.current_page = "risques"
                    st.rerun()
        else:
            if st.button("⚠️ Voir les risques", type="primary", use_container_width=True):
                st.session_state.current_page = "risques"
                st.rerun()
    
    st.stop()


# ===== PAGE LIENS ALOE =====
if st.session_state.current_page == "aloe_links" and st.session_state.aloe_links_done:
    result = st.session_state.result
    
    st.subheader("🔗 Liens ALOE extraits")
    
    if result.get("page_aloe_links"):
        for page_data in result["page_aloe_links"]:
            with st.expander(f"📄 Page {page_data['page_num']}", expanded=True):
                links = page_data.get("links", [])
                
                if not links:
                    st.info("Aucun lien ALOE identifié sur cette page")
                    continue
                
                for link in links:
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        st.markdown(f"**🔵 {link.get('source_object', 'N/A')}**")
                        st.caption(f"Attribut : `{link.get('source_attribute', '')}`")
                    
                    with col2:
                        link_type = link.get("link_type", "→")
                        st.markdown(
                            f"<div style='text-align:center; padding-top:8px; font-weight:bold;'>⟶<br/><small>{link_type}</small></div>",
                            unsafe_allow_html=True
                        )
                    
                    with col3:
                        st.markdown(f"**🔵 {link.get('target_object', 'N/A')}**")
                        st.caption(f"Attribut : `{link.get('target_attribute', '')}`")
                    
                    if link.get("justification"):
                        st.caption(f"📝 {link['justification']}")
                    
                    st.markdown("---")
    else:
        st.info("Aucune extraction de liens ALOE disponible")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.current_page = "aloe"
            st.rerun()
    with col2:
        if not st.session_state.aloe_vulnerabilities_done:
            if st.button("➡️ Analyser les vulnérabilités ALOE", type="primary", use_container_width=True):
                with st.spinner("🔄 Analyse des vulnérabilités ALOE en cours..."):
                    result = st.session_state.graph.invoke(None, st.session_state.config)
                    st.session_state.result = result
                    st.session_state.aloe_vulnerabilities_done = True
                    st.session_state.current_page = "aloe_vulnerabilities"
                    st.rerun()
        else:
            if st.button("🛡️ Voir les vulnérabilités", type="primary", use_container_width=True):
                st.session_state.current_page = "aloe_vulnerabilities"
                st.rerun()
    
    st.stop()


# ===== PAGE ALOE =====
if st.session_state.current_page == "aloe" and st.session_state.aloe_done:
    result = st.session_state.result
    
    st.subheader("🎯 Objets ALOE extraits")
    
    if result.get("page_aloe_objects"):
        for page_data in result["page_aloe_objects"]:
            with st.expander(f"📄 Page {page_data['page_num']}", expanded=True):
                
                if not page_data["aloe_objects"]:
                    st.info("Aucun objet ALOE identifié sur cette page")
                    continue
                
                for obj in page_data["aloe_objects"]:
                    st.markdown(f"### {obj['object_name']}")
                    st.markdown(f"**Catégorie :** {obj['category']}")
                    
                    st.markdown("**Attributs :**")
                    for attr in obj["attributes"]:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"- **{attr['name']}**")
                        with col2:
                            if attr.get("value"):
                                st.markdown(f"Valeur : `{attr['value']}`")
                            st.caption(f"📝 {attr['justification']}")
                    
                    st.caption(f"📌 {obj['justification']}")
                    st.markdown("---")
    else:
        st.info("Aucune extraction ALOE disponible")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.current_page = "accueil"
            st.rerun()
    with col2:
        if not st.session_state.aloe_links_done:
            if st.button("➡️ Extraire les liens ALOE", type="primary", use_container_width=True):
                with st.spinner("🔄 Extraction des liens ALOE en cours..."):
                    result = st.session_state.graph.invoke(None, st.session_state.config)
                    st.session_state.result = result
                    st.session_state.aloe_links_done = True
                    st.session_state.current_page = "aloe_links"
                    st.rerun()
        else:
            if st.button("🔗 Voir les liens ALOE", type="primary", use_container_width=True):
                st.session_state.current_page = "aloe_links"
                st.rerun()
    
    st.stop()


# ===== PAGE VOIR PAGES =====
if st.session_state.current_page == "voir_pages" and st.session_state.extraction_done:
    result = st.session_state.result
    
    display_pages_as_word(result["pages"], result["total_pages"])
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour à l'accueil", use_container_width=True):
            st.session_state.current_page = "accueil"
            st.rerun()
    with col2:
        if not st.session_state.summarization_done:
            if st.button("➡️ Lancer les analyses", type="primary", use_container_width=True):
                with st.spinner("🔄 Résumé + extraction ALOE en cours..."):
                    result = st.session_state.graph.invoke(None, st.session_state.config)
                    st.session_state.result = result
                    st.session_state.summarization_done = True
                    st.session_state.aloe_done = True
                    st.session_state.current_page = "aloe"
                    st.rerun()
        else:
            if st.button("🎯 Voir objets ALOE", type="primary", use_container_width=True):
                st.session_state.current_page = "aloe"
                st.rerun()
    
    st.stop()


# ===== PAGE ACCUEIL =====
st.subheader("1️⃣ Importer votre document")

uploaded_file = st.file_uploader(
    "Déposez votre PDF ou DOCX",
    type=["pdf", "docx"],
    help="Document de projet à analyser"
)

if uploaded_file and not st.session_state.extraction_done:
    temp_dir = Path("data/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / uploaded_file.name
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    
    if st.button("🚀 Lancer l'extraction", type="primary", use_container_width=True):
        with st.spinner("🔄 Extraction en cours..."):
            try:
                initial_state = MainState(
                    uploaded_file_path=str(temp_path),
                    file_name=uploaded_file.name,
                    file_type=uploaded_file.name.split('.')[-1],
                    upload_status="pending",
                    extraction_status="pending",
                    pages=[],
                    total_pages=0,
                    raw_text="",
                    extraction_time=0.0,
                    llama_parse_job_id=None,
                    edit_mode=None,
                    target_page_num=None,
                    edit_instruction=None,
                    edited_pages=[],
                    edit_history=[],
                    current_page_index=0,
                    page_summaries=[],
                    global_summary="",
                    current_aloe_page_index=0,
                    page_aloe_objects=[],
                    all_extracted_aloe_objects=[],
                    current_aloe_links_page_index=0,
                    page_aloe_links=[],
                    current_aloe_vulnerability_page_index=0,
                    page_aloe_vulnerabilities=[],
                    error_message=None,
                    current_risk_page_index=0,
                    page_risks=[],
                    all_identified_elements=[],
                    all_identified_threats=[]
                )
                
                result = st.session_state.graph.invoke(initial_state, st.session_state.config)
                st.session_state.result = result
                st.session_state.extraction_done = True
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ {str(e)}")

# Si extraction terminée, affichage accueil
if st.session_state.extraction_done and st.session_state.current_page == "accueil":
    result = st.session_state.result
    
    if result.get("extraction_status") == "completed":
        st.success("✅ Extraction terminée !")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages extraites", result['total_pages'])
        with col2:
            st.metric("Temps", f"{result['extraction_time']:.1f}s")
        with col3:
            total_words = sum(len(p['content'].split()) for p in result['pages'])
            st.metric("Mots", f"{total_words:,}")
        
        st.markdown("---")
        
        # Pipeline de progression
        st.markdown("### 🗺️ Pipeline d'analyse")
        
        steps = [
            ("✅ Extraction", True),
            ("🎯 Résumé + ALOE", st.session_state.aloe_done),
            ("🔗 Liens ALOE", st.session_state.aloe_links_done),
            ("🛡️ Vulnérabilités ALOE", st.session_state.aloe_vulnerabilities_done),
            ("⚠️ Risques", st.session_state.risks_done),
        ]
        
        cols = st.columns(len(steps))
        for col, (label, done) in zip(cols, steps):
            with col:
                if done:
                    st.success(label)
                else:
                    st.warning(label)
        
        st.markdown("---")
        st.markdown("### 2️⃣ Étape suivante")
        
        if st.button("📄 Voir les pages extraites", type="primary", use_container_width=True):
            st.session_state.current_page = "voir_pages"
            st.rerun()