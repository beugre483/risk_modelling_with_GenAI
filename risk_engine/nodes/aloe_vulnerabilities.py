# nodes/aloe_vulnerabilities.py

from ..core.state import MainState
from ..core.schema import ALOEVulnerabilityOutput
from ..services.llm_client import get_llm
from typing import Dict
import json


def extract_aloe_vulnerabilities_node(state: MainState) -> Dict:
    """
    Identifie les vulnérabilités ALOE page par page
    """
    idx = state.get("current_aloe_vulnerability_page_index", 0)
    
    if idx >= state["total_pages"]:
        return {**state}
    
    current_page_summary = state["page_summaries"][idx]["summary"]
    
    # Récupère objets ALOE et liens de cette page
    current_aloe_objects = []
    current_links = []
    
    for page_data in state.get("page_aloe_objects", []):
        if page_data["page_num"] == idx + 1:
            current_aloe_objects = page_data["aloe_objects"]
            break
    
    for page_data in state.get("page_aloe_links", []):
        if page_data["page_num"] == idx + 1:
            current_links = page_data["links"]
            break
    
    if not current_aloe_objects:
        return {
            **state,
            "current_aloe_vulnerability_page_index": idx + 1
        }
    
    llm = get_llm()
    
    objects_str = json.dumps(current_aloe_objects, indent=2, ensure_ascii=False)
    links_str = json.dumps(current_links, indent=2, ensure_ascii=False)
    
    prompt = f"""Vous êtes un expert en analyse de risques selon la méthode ALOE.

Votre mission est d'identifier les vulnérabilités des objets ALOE en tenant compte de leurs liens.

DONNEES:

PAGE: {idx + 1} sur {state['total_pages']}

Résumé global:
{state.get('global_summary', 'Non disponible')}

Résumé page actuelle:
{current_page_summary}

Objets ALOE:
{objects_str}

Liens entre objets:
{links_str}
LEXIQUE ALOE DETAILLE:

OBJET ALOE:
Composant concret ou abstrait du projet qui peut:
- être directement impacté par une menace
- transmettre un impact à d'autres éléments du projet
- influencer l'atteinte des objectifs

Categories d'objets ALOE:

1. OBJECTIF: Résultat précis à atteindre dans le cadre du projet
   Exemples: Objectif de livraison d'un bâtiment, Objectif de conformité réglementaire

2. ACTIVITE / PROCESSUS: Actions, opérations ou tâches à réaliser
   Exemples: Activité de construction, Processus d'analyse des effluents

3. ORGANISATION / ACTEUR: Entité humaine ou structure organisationnelle intervenant dans le projet
   Exemples: Équipe projet, Sous-traitant, Cellule qualité

4. RESSOURCE: Moyens nécessaires à l'exécution du projet
   Exemples: Ressource matérielle comme une grue, Ressource financière comme un budget alloué

5. LIVRABLE / PRODUIT: Résultat matériel ou immatériel issu du projet
   Exemples: Rapport technique, Ouvrage construit, Logiciel opérationnel

ATTRIBUTS ALOE:
Caractéristiques spécifiques et mesurables de l'objet qui peuvent être dégradées ou perturbées:

- Coût (€): impact financier potentiel
- Durée (jours, mois...): délai nécessaire pour accomplir ou livrer l'objet
- Qualité: conformité ou respect des exigences
- Date de début/fin: calendrier précis
- Avancement (%): état d'avancement réel par rapport au prévu
- Description/Spécifications: caractéristiques ou propriétés attendues
- Ressources allouées: moyens spécifiques affectés à l'objet
- Valeur ajoutée: bénéfice attendu par rapport aux objectifs stratégiques


DEFINITIONS DES TYPES DE LIENS ALOE:

1. Contribution: Un objet facilite ou soutient activement la réalisation ou la réussite d'un autre objet.

2. Séquentiel: Un objet doit être achevé avant que l'autre puisse démarrer.

3. Influence: Un objet affecte significativement l'état ou les attributs d'un autre, modifiant son coût, sa qualité ou son délai.

4. Échange: Deux objets échangent des informations, ressources ou services nécessaires à leur fonctionnement respectif.


TÂCHE:

Pour chaque objet ALOE:
1. Identifiez quel attribut est vulnérable
2. Identifiez la menace qui peut l'attaquer
3. Si l'objet est lié à d'autres, décrivez comment la menace peut se propager via ces liens
4. Justifiez basé sur le contexte

EXEMPLE:

{{
  "aloe_object_name": "Budget finitions",
  "vulnerable_attribute": "Coût",
  "threat": "Inflation matériaux",
  "propagation_path": "Budget finitions → Activité pose (Séquentiel) → Délai global (Influence)",
  "justification": "Budget contraint à 5%, toute inflation épuise la marge et retarde la pose, impactant le délai global"
}}

REPONSE:
Format JSON selon ALOEVulnerabilityOutput.
"""
    
    vuln_data = llm.invoke_structured(prompt, ALOEVulnerabilityOutput)
    
    page_vuln_entry = {
        "page_num": idx + 1,
        "vulnerabilities": [v.model_dump() for v in vuln_data.vulnerable_elements]
    }
    
    return {
        **state,
        "page_aloe_vulnerabilities": state.get("page_aloe_vulnerabilities", []) + [page_vuln_entry],
        "current_aloe_vulnerability_page_index": idx + 1,
        "error_message": None
    }


def should_continue_aloe_vulnerabilities(state: MainState) -> str:
    """Continue ou fini ?"""
    if state.get("current_aloe_vulnerability_page_index", 0) >= state["total_pages"]:
        return "finish"
    return "continue"