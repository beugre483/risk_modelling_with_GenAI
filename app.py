import streamlit as st
from pathlib import Path
import sys
import os

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.append(str(Path(__file__).parent))

from risk_engine.graphs.main_graph import create_main_graph
from risk_engine.core.state import MainState
from ui.page_viewer import display_pages_as_word

st.set_page_config(
    page_title="Analyseur de Risques Projet",
    page_icon="📊",
    layout="wide"
)

def load_css():
    css_file = Path(__file__).parent / "ui" / "style.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .stButton>button {width: 100%; border-radius: 5px;}
        </style>
        """, unsafe_allow_html=True)

load_css()

if "graph" not in st.session_state:
    st.session_state.graph = create_main_graph()

if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "session_001"}}

if "result" not in st.session_state:
    st.session_state.result = None

if "extraction_done" not in st.session_state:
    st.session_state.extraction_done = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"


# --- HELPER : lecture sécurisée du résultat ---
def safe_get(res, key, default=None):
    """Lit une clé depuis un dict ou un objet LangGraph AddableValuesDict."""
    if res is None:
        return default
    try:
        if isinstance(res, dict):
            return res.get(key, default)
        return getattr(res, key, default)
    except Exception:
        return default


# --- HELPER : liste des nœuds suivants ---
def get_next_nodes(snapshot):
    """Retourne une liste de chaînes des prochains nœuds du graph."""
    try:
        if snapshot is None or snapshot.next is None:
            return []
        return list(snapshot.next)
    except Exception:
        return []


# --- SIDEBAR & SÉCURITÉ API ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("### 🔑 Clés API")

    if "mistral_key" not in st.session_state:
        st.session_state.mistral_key = ""
    if "llama_key" not in st.session_state:
        st.session_state.llama_key = ""

    mistral_input = st.text_input("Clé API Mistral", value=st.session_state.mistral_key, type="password")
    llama_input = st.text_input("Clé API Llama Cloud", value=st.session_state.llama_key, type="password")

    if mistral_input:
        os.environ["MISTRAL_API_KEY"] = mistral_input
        st.session_state.mistral_key = mistral_input

    if llama_input:
        os.environ["LLAMA_CLOUD_API_KEY"] = llama_input
        st.session_state.llama_key = llama_input

    keys_configured = mistral_input and llama_input

    st.markdown("---")

    if st.session_state.extraction_done:
        st.markdown("### 📑 Navigation")

        if st.button("🏠 Accueil / Upload", use_container_width=True):
            st.session_state.current_page = "accueil"
            st.rerun()

        if st.button("📄 Voir les pages", use_container_width=True):
            st.session_state.current_page = "voir_pages"
            st.rerun()

        if st.button("🧠 Compréhension", use_container_width=True):
            st.session_state.current_page = "resume"
            st.rerun()

        if st.button("⚠️ Risques", use_container_width=True):
            st.session_state.current_page = "risques"
            st.rerun()


# --- BLOCAGE SI PAS DE CLÉS ---
if not keys_configured:
    st.warning("⚠️ VEUILLEZ D'ABORD ENTRER VOS CLÉS API DANS LA BARRE LATÉRALE (à gauche).")
    st.info("Sans clé LlamaCloud, impossible de lire le PDF. Sans clé Mistral, impossible de l'analyser.")
    st.stop()


# ============================================================
# PAGE : ACCUEIL
# ============================================================
if st.session_state.current_page == "accueil":
    st.title("📊 Analyseur de Risques de Projet")
    st.markdown("---")

    st.subheader("1️⃣ Importer votre document")
    uploaded_file = st.file_uploader("Déposez votre PDF ou DOCX", type=["pdf", "docx"])

    if uploaded_file:
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / uploaded_file.name

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Fichier prêt : {uploaded_file.name}")

        if st.button("🚀 Lancer l'extraction", type="primary"):
            with st.spinner("Extraction en cours..."):
                try:
                    initial_state = MainState(
                        uploaded_file_path=str(temp_path),
                        file_name=uploaded_file.name,
                        file_type=uploaded_file.name.split('.')[-1],
                        upload_status="pending", extraction_status="pending",
                        pages=[], total_pages=0, raw_text="", extraction_time=0.0,
                        llama_parse_job_id=None,
                        page_summaries=[], global_summary="",
                        page_risks=[], all_identified_elements=[], all_identified_threats=[],
                        current_page_index=0, current_risk_page_index=0,
                        edit_mode=None, target_page_num=None, edit_instruction=None,
                        edited_pages=[], edit_history=[], error_message=None
                    )
                    result = st.session_state.graph.invoke(initial_state, st.session_state.config)

                    st.session_state.result = result
                    st.session_state.extraction_done = True
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'extraction : {str(e)}")

    if st.session_state.extraction_done:
        res = st.session_state.result
        if res and safe_get(res, "extraction_status") == "completed":
            st.success("✅ Extraction terminée !")
            c1, c2 = st.columns(2)
            c1.metric("Pages", safe_get(res, "total_pages", 0))
            c2.metric("Temps", f"{safe_get(res, 'extraction_time', 0):.2f}s")

            st.info("Document prêt.")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Aller voir les pages 📄", use_container_width=True):
                    st.session_state.current_page = "voir_pages"
                    st.rerun()
            with col_b:
                if st.button("Passer à la compréhension 🧠", use_container_width=True):
                    st.session_state.current_page = "resume"
                    st.rerun()


# ============================================================
# PAGE : VOIR PAGES
# ============================================================
elif st.session_state.current_page == "voir_pages":
    st.header("📄 Visualisation du document")

    res = st.session_state.result
    pages = safe_get(res, "pages")
    total_pages = safe_get(res, "total_pages", 0)

    if pages:
        display_pages_as_word(pages, total_pages)
    else:
        st.warning("Aucune page à afficher.")

    if st.button("⬅️ Retour"):
        st.session_state.current_page = "accueil"
        st.rerun()


# ============================================================
# PAGE : RESUME (Compréhension du contexte)
# ============================================================
elif st.session_state.current_page == "resume":
    st.header("🧠 Compréhension du contexte")

    res = st.session_state.result

    # Récupération sécurisée du snapshot
    try:
        snapshot = st.session_state.graph.get_state(st.session_state.config)
        next_nodes = get_next_nodes(snapshot)
    except Exception as e:
        st.error(f"Impossible de lire l'état du graph : {e}")
        st.stop()

    global_summary = safe_get(res, "global_summary", "")
    total_pages = safe_get(res, "total_pages", 0)

    # CAS 1 : Le graph attend le lancement de la résumé
    ready_to_summarize = any("summarize" in node for node in next_nodes)

    if ready_to_summarize:
        st.info(f"L'IA va analyser les {total_pages} pages pour comprendre le projet.")

        if st.button("▶️ Lancer l'analyse contextuelle", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                for update in st.session_state.graph.stream(None, st.session_state.config):
                    if 'summarize_page' in update:
                        current_state = update['summarize_page']
                        current_idx = current_state.get("current_page_index", 0)
                        progress = min(current_idx / total_pages, 1.0) if total_pages > 0 else 0
                        progress_bar.progress(progress)
                        status_text.write(f"⏳ Analyse de la page {current_idx} / {total_pages}...")

                final_state = st.session_state.graph.get_state(st.session_state.config).values
                st.session_state.result = final_state
                st.rerun()

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

    # CAS 2 : L'analyse est déjà terminée
    elif global_summary:
        st.success("Analyse terminée.")

        with st.expander("🌍 Résumé Global", expanded=True):
            st.markdown(global_summary)

        st.subheader("Détail par page")
        page_summaries = safe_get(res, "page_summaries", [])
        if page_summaries:
            tabs = st.tabs([f"Page {p['page_num']}" for p in page_summaries])
            for i, tab in enumerate(tabs):
                with tab:
                    st.write(page_summaries[i]["summary"])

        if st.button("Passer aux Risques ➡️", type="primary"):
            st.session_state.current_page = "risques"
            st.rerun()

    # CAS 3 : État indéterminé — on affiche un diagnostic au lieu d'un message vague
    else:
        st.warning("Le graph n'est pas encore prêt pour cette étape.")
        st.markdown("**Diagnostic :**")
        st.code(f"Nœuds suivants détectés : {next_nodes}", language="text")
        st.code(f"global_summary présent : {bool(global_summary)}", language="text")
        st.info("Si l'extraction vient d'être faite, cliquez sur le bouton ci-dessous pour forcer la reprise.")

        if st.button("🔄 Rafraîchir l'état"):
            try:
                final_state = st.session_state.graph.get_state(st.session_state.config).values
                st.session_state.result = final_state
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")


# ============================================================
# PAGE : RISQUES
# ============================================================
elif st.session_state.current_page == "risques":
    st.header("⚠️ Identification des Risques")

    res = st.session_state.result

    # Récupération sécurisée du snapshot
    try:
        snapshot = st.session_state.graph.get_state(st.session_state.config)
        next_nodes = get_next_nodes(snapshot)
    except Exception as e:
        st.error(f"Impossible de lire l'état du graph : {e}")
        st.stop()

    total_pages = safe_get(res, "total_pages", 0)
    page_risks = safe_get(res, "page_risks", [])

    # CAS 1 : Le graph attend le lancement de l'analyse des risques
    ready_to_analyze = any("risk" in node for node in next_nodes)

    if ready_to_analyze:
        st.info("L'IA va croiser les informations pour détecter les vulnérabilités.")

        if st.button("▶️ Lancer l'identification", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                for update in st.session_state.graph.stream(None, st.session_state.config):
                    if 'analyze_risk_page' in update:
                        current_state = update['analyze_risk_page']
                        current_idx = current_state.get("current_risk_page_index", 0)
                        progress = min(current_idx / total_pages, 1.0) if total_pages > 0 else 0
                        progress_bar.progress(progress)
                        status_text.write(f"⏳ Analyse des risques page {current_idx} / {total_pages}...")

                final_state = st.session_state.graph.get_state(st.session_state.config).values
                st.session_state.result = final_state
                st.rerun()

            except Exception as e:
                st.error(f"Erreur durant l'analyse : {e}")

    # CAS 2 : L'analyse des risques est terminée
    elif page_risks:
        st.success("Analyse des risques terminée.")

        total_risks = sum(len(p.get('vulnerable_elements', [])) for p in page_risks)
        st.metric("Total éléments vulnérables identifiés", total_risks)

        for p_risk in page_risks:
            nb_risks = len(p_risk.get('vulnerable_elements', []))
            if nb_risks > 0:
                with st.expander(f"Page {p_risk['page_num']} ({nb_risks} éléments)", expanded=True):
                    for ve in p_risk.get('vulnerable_elements', []):
                        st.markdown(f"**🔹 Élément vulnérable :** {ve.get('element', 'N/A')}")
                        st.markdown(f"**Justification :** {ve.get('justification', 'N/A')}")
                        st.markdown("---")

                    for ta in p_risk.get('threat_associations', []):
                        st.markdown(f"**🔴 Menace :** {ta.get('threat', 'N/A')}")
                        st.markdown(f"**Justification :** {ta.get('justification', 'N/A')}")
                        st.markdown(f"**Impact :** {ta.get('potential_impact', 'N/A')}")
                        st.markdown("---")
            else:
                with st.expander(f"Page {p_risk['page_num']} (R.A.S)", expanded=False):
                    st.write("Aucun risque majeur identifié sur cette page.")

    # CAS 3 : État indéterminé
    else:
        st.warning("Le graph n'est pas encore prêt pour l'analyse des risques.")
        st.markdown("**Diagnostic :**")
        st.code(f"Nœuds suivants détectés : {next_nodes}", language="text")
        st.info("Assurez-vous d'avoir complété l'étape **Compréhension** avant de lancer les risques.")

        if st.button("🔄 Rafraîchir l'état"):
            try:
                final_state = st.session_state.graph.get_state(st.session_state.config).values
                st.session_state.result = final_state
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")