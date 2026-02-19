# nodes/summarization.py

from ..core.state import MainState
from ..core.schema import SummaryOutput
from ..services.llm_client import get_llm
from typing import Dict


def summarize_page_node(state: MainState) -> Dict:
    """
    Résume la page courante avec contexte cumulatif - Phase de compréhension du système
    """
    idx = state.get("current_page_index", 0)
    
    # Vérifie si terminé
    if idx >= state["total_pages"]:
        return {**state}
    
    current_page = state["pages"][idx]
    llm = get_llm()
    
    prompt = f"""Tu es un assistant expert en gestion de risques de projets.

PHASE ACTUELLE: COMPRÉHENSION DU SYSTÈME
Tu es dans la phase initiale d'analyse où tu dois collecter et structurer les informations pour préparer l'identification des risques. Cette phase ne consiste PAS à identifier les risques, mais à COMPRENDRE le projet dans ses moindres détails.

CONTEXTE:
- Page en cours: {current_page['page_num']} sur {state['total_pages']}
- Tu construis progressivement une cartographie complète du projet

DONNÉES DISPONIBLES:
Résumé global (pages 1 à {idx}):
{state.get('global_summary', 'Première page - pas de contexte antérieur')}

Contenu de la page actuelle:
{current_page['content']}

TA MISSION - COLLECTE D'INFORMATIONS:

PRIORITÉ 1: Résume TOUT le contenu factuel de cette page
- Peu importe le sujet: résume fidèlement ce qui est écrit
- Même si ça ne rentre pas dans les catégories ci-dessous, capture l'information

SI LA PAGE CONTIENT des informations sur ces dimensions, extrais-les particulièrement:
1. Périmètre & Objectifs (objectifs, KPIs, livrables, jalons)
2. Acteurs & Responsabilités (parties prenantes, rôles, dépendances)
3. Ressources & Contraintes (budget, RH, infrastructure, outils)
4. Planification & Dépendances (calendrier, phases, dépendances externes, hypothèses)
5. Gouvernance & Processus (décisions, validations, contrôles)

ZONES D'ATTENTION:
Si tu repères des informations manquantes ou des hypothèses non validées, note-les:
✓ "Budget sans détail sur les sources"
✓ "Calendrier basé sur hypothèse de disponibilité"
✗ "RISQUE financier" → NON, pas d'analyse formelle

RÉSUMÉS À PRODUIRE:

1. page_summary (5-8 phrases):
   - Résume TOUT ce qui est dans cette page
   - Si des dimensions clés apparaissent, structure autour d'elles
   - Sinon, résume simplement le contenu tel quel
   - Mentionne les zones d'attention si pertinent
   - Autonome et factuel

2. global_summary (vue d'ensemble):
   - Synthèse cumulative enrichie de cette nouvelle page
   - Intègre le nouveau contenu au contexte existant
   - Vision cohérente du projet qui se construit
   - Sans répétition mot-à-mot

PRINCIPES:
- Résume TOUJOURS le contenu, même s'il ne rentre dans aucune catégorie
- Sois factuel: base-toi uniquement sur ce qui est écrit
- Sois exhaustif: ne perds aucune information
- Sois neutre: pas d'interprétation

SORTIE ATTENDUE:
JSON valide uniquement:
{{
  "page_summary": "",
  "global_summary": ""
}}
"""
    
    # Utilise invoke_structured avec le schéma Pydantic
    summaries = llm.invoke_structured(prompt, SummaryOutput)
    
    # Sauvegarde le résumé de la page
    new_page_summary = {
        "page_num": current_page["page_num"],
        "summary": summaries.page_summary
    }
    
    return {
        **state,
        "page_summaries": state.get("page_summaries", []) + [new_page_summary],
        "global_summary": summaries.global_summary,
        "current_page_index": idx + 1,
        "error_message": None
    }


def should_continue_summary(state: MainState) -> str:
    """Continue ou fini ?"""
    if state.get("current_page_index", 0) >= state["total_pages"]:
        return "finish"
    return "continue"