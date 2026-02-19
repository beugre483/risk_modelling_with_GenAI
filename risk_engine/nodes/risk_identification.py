from ..core.state import MainState
from ..core.schema import RiskAnalysisOutput
from ..services.llm_client import get_llm
from typing import Dict

def analyze_risks_page_node(state: MainState) -> Dict:
    """
    Analyse les risques page par page de manière cumulative
    """
    idx = state.get("current_risk_page_index", 0)
    
    if idx >= state["total_pages"]:
        return {**state}
    
    current_page = state["pages"][idx]
    current_page_summary = state["page_summaries"][idx]["summary"]
    
    last_page_summary = ""
    if idx > 0:
        last_page_summary = state["page_summaries"][idx - 1]["summary"]
    
    already_identified = "\n".join([
        f"- {elem}" for elem in state.get("all_identified_elements", [])
    ])
    
    llm = get_llm()
    
    prompt = f"""Tu es un expert en gestion de risques de projets.

Un RISQUE PROJET est un événement futur incertain ayant un impact négatif sur les objectifs du projet (qualité, coût, délai).

DEFINITIONS FONDAMENTALES (à appliquer strictement) :

- ELEMENT VULNERABLE : une composante du projet (ressource, activité, livrable, organisation, infrastructure) qui, en raison de sa fragilité, complexité, ou dépendance, peut être affectée par une menace. Il peut être fragilisé ou perturber le projet s'il est attaqué ou perturbé.

- MENACE : un événement, facteur interne ou externe, qui pourrait exploiter une vulnérabilité pour provoquer un dommage. Elle agit sur un élément vulnérable.

- CONSEQUENCE : l'impact que cela aurait sur les objectifs du projet (délai, coût, qualité).

- RISQUE : une formulation logique complète qui relie un élément vulnérable, une menace précise, et un impact.

CONTEXTE DE TRAVAIL - Analyse page par page :

Tu vas analyser un document de projet très long.
Tu dois donc travailler page par page, mais en gardant la cohérence avec ce qui a déjà été traité auparavant.

Tu reçois les informations suivantes à chaque étape :

1. globalSummary : résumé cumulé des pages précédentes, il t'aide à ne pas répéter des éléments déjà identifiés et à garder la vision d'ensemble du projet.

2. lastPageSummary : résumé détaillé de la dernière page analysée, pour rester dans le même fil logique et assurer la continuité.

3. currentPageSummary : résumé de la page actuelle, pour repérer rapidement les zones à risque potentielles.

4. pageContent : contenu de la page actuelle à analyser. C'EST ICI que tu extrais les éléments vulnérables et que tu justifies chaque identification.

5. alreadyIdentified : liste des éléments vulnérables déjà identifiés dans les pages précédentes. CRITIQUE : ne JAMAIS répéter un élément de cette liste.

IMPORTANT :
- Tu ne dois jamais extraire deux fois un même élément vulnérable ou une menace déjà citée dans les pages précédentes.
- Tu ne dois analyser que le contenu de la page actuelle (pageContent), en tenant compte du fil conducteur (globalSummary et lastPageSummary).
- Tu ne dois extraire que les éléments qui sont concrets, spécifiques et sensibles, qui peuvent impacter significativement le projet.

DONNEES RECUES POUR CETTE ITERATION :

PAGE EN COURS : {current_page['page_num']} sur {state['total_pages']}

globalSummary (pages 1 à {idx}) :
{state.get('global_summary', 'Première page - pas de contexte antérieur')}

lastPageSummary (page {idx}) :
{last_page_summary if last_page_summary else 'Aucune page précédente'}

currentPageSummary (page {current_page['page_num']}) :
{current_page_summary}

pageContent (contenu complet page {current_page['page_num']}) :
{current_page['content']}

alreadyIdentified (éléments vulnérables déjà identifiés - NE PAS REPETER) :
{already_identified if already_identified else 'Aucun élément identifié dans les pages précédentes'}

OBJECTIF - Ta mission est structurée en deux étapes :

ETAPE 1 - Identifier les éléments vulnérables présents dans la page

- Ne garde que ceux qui sont concrets, spécifiques, sensibles, liés à des ressources, activités, contraintes ou installations.
- Chaque élément vulnérable doit être justifié par un extrait ou une paraphrase du document, avec une explication claire de sa vulnérabilité.
- Exclus les éléments déjà dans alreadyIdentified.
- Exclus les concepts vagues comme "le projet", "la qualité", "les risques techniques".

Format attendu :
- Élément vulnérable : [nom synthétique]
  Justification : [extrait ou paraphrase du document + explication du pourquoi cet élément est fragile]

Exemple :
Élément vulnérable : Budget de finition trop serré
Justification : "Le budget alloué aux finitions représente seulement 5% du coût total du projet" → cette marge réduite limite la flexibilité en cas de hausse des prix ou d'ajout de spécifications.

ETAPE 2 - Associer une ou plusieurs menaces à chaque élément vulnérable

- Pour chaque élément identifié à l'étape 1, propose au moins une menace potentielle qui pourrait l'exploiter.
- La menace peut venir d'un facteur externe (climat, acteur tiers, accident, faillite fournisseur, régulation) ou d'un facteur interne (erreur humaine, défaillance technique, turnover, sous-estimation).

Format attendu :
- Élément vulnérable : [nom exact de l'étape 1]
  Menace associée : [description claire de l'événement]
  Justification : [lien logique entre menace et vulnérabilité]
  Impact potentiel : [effet sur délai, coût ou qualité]

Exemple :
Élément vulnérable : Budget de finition trop serré
Menace associée : Dépassement des coûts de matériaux
Justification : Une inflation de 10% sur les peintures et revêtements non prévue dans l'estimation initiale épuisera la ligne budgétaire, forçant à des arbitrages qui pourraient dégrader la qualité.
Impact potentiel : Dégradation de la qualité des finitions et dépassement budgétaire.

ATTENTION - ASSURE-TOI QUE :
- Toutes les menaces sont reliées à un élément vulnérable clair
- Aucun élément n'est vague ou redondant avec ceux déjà dans alreadyIdentified
- Tu restes strictement lié au contenu de la page actuelle, avec le contexte en soutien, mais sans extrapolation excessive
- Chaque identification a une justification textuelle basée sur pageContent

Souviens-toi : tu travailles page par page, en évitant les redites, et en construisant une analyse cumulative, progressive et logique.

REPONSE ATTENDUE :
Format JSON uniquement, sans texte avant ou après.
Respecte le schéma RiskAnalysisOutput.
"""
    
    risks = llm.invoke_structured(prompt, RiskAnalysisOutput)
    
    new_elements = [ve.element for ve in risks.vulnerable_elements]
    
    page_risk_entry = {
        "page_num": current_page["page_num"],
        "vulnerable_elements": [ve.model_dump() for ve in risks.vulnerable_elements],
        "threat_associations": [ta.model_dump() for ta in risks.threat_associations]
    }
    
    return {
        **state,
        "page_risks": state.get("page_risks", []) + [page_risk_entry],
        "all_identified_elements": state.get("all_identified_elements", []) + new_elements,
        "current_risk_page_index": idx + 1,
        "error_message": None
    }


def should_continue_risk_analysis(state: MainState) -> str:
    """Continue ou fini ?"""
    if state.get("current_risk_page_index", 0) >= state["total_pages"]:
        return "finish"
    return "continue"