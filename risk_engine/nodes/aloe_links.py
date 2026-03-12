
# nodes/aloe_links.py

from ..core.state import MainState
from ..core.schema import ALOELinksOutput
from ..services.llm_client import get_llm
from typing import Dict


def extract_aloe_links_node(state: MainState) -> Dict:
    """
    Extrait les liens entre objets ALOE page par page.
    Utilise UNIQUEMENT les objets déjà extraits dans all_extracted_aloe_objects.
    """
    idx = state.get("current_aloe_links_page_index", 0)

    if idx >= state["total_pages"]:
        return {**state}

    current_page = state["pages"][idx]
    current_page_summary = state["page_summaries"][idx]["summary"]

    last_page_summary = ""
    if idx > 0:
        last_page_summary = state["page_summaries"][idx - 1]["summary"]

    # Liste des objets déjà extraits — le LLM DOIT réutiliser ces noms exacts
    all_objects = state.get("all_extracted_aloe_objects", [])
    objects_list = "\n".join(f"- {name}" for name in all_objects)

    llm = get_llm()

    prompt = f"""Vous êtes un spécialiste de la méthode ALOE, une approche structurée d'analyse des risques dans des projets complexes.

CONTEXTE - Extraction des liens ALOE page par page:

PAGE EN COURS: {current_page['page_num']} sur {state['total_pages']}

DONNÉES DISPONIBLES:

1. RÉSUMÉ GLOBAL (pages 1 à {idx}):
{state.get('global_summary', 'Première page - pas de contexte antérieur')}

2. RÉSUMÉ PAGE PRÉCÉDENTE (page {idx}):
{last_page_summary if last_page_summary else 'Aucune page précédente'}

3. RÉSUMÉ PAGE ACTUELLE (page {current_page['page_num']}):
{current_page_summary}

4. CONTENU COMPLET PAGE ACTUELLE:
{current_page['content']}

5. OBJETS ALOE IDENTIFIÉS (utilise UNIQUEMENT ces noms exacts):
{objects_list if objects_list else 'Aucun objet extrait précédemment'}

LEXIQUE DES TYPES DE LIENS ALOE:

1. SÉQUENTIEL: L'objet source doit être achevé avant que l'objet cible puisse démarrer.
   Exemple: "Études AVP" → "Études PRO"

2. CONTRIBUTION: L'objet source participe activement à la réalisation ou au succès de l'objet cible.
   Exemple: "Équipe projet" → "Plan de management de projet"

3. INFLUENCE: L'objet source affecte positivement ou négativement l'objet cible sans en être un prérequis direct.
   Exemple: "Augmentation de l'offre de transport" → "Réduction des émissions"

VOTRE MISSION:

Identifier tous les liens logiques entre les objets ALOE listés ci-dessus,
à partir du contenu de la page actuelle.

Pour chaque lien identifié:
1. Sélectionnez source_object et target_object PARMI la liste des objets ALOE fournie
2. Choisissez le type de lien (Séquentiel, Contribution, Influence)
3. Indiquez les attributs concernés si mentionnés (sinon laisser vide)
4. Justifiez par une citation ou paraphrase du document

RÈGLES STRICTES:

- Utiliser UNIQUEMENT les noms d'objets présents dans la liste "OBJETS ALOE IDENTIFIÉS"
- Ne PAS inventer de nouveaux objets
- Ne PAS modifier les noms des objets (copier-coller exact)
- Chaque lien doit être justifié par le contenu de la page
- Un même objet peut apparaître dans plusieurs liens

EXEMPLES DE LIENS:

Texte: "Les études AVP doivent être finalisées avant le dépôt du dossier d'enquête publique"
→ source_object: "Études d'avant-projet (AVP)"
→ target_object: "Dossier d'enquête publique"
→ link_type: "Séquentiel"
→ justification: "Les études AVP doivent être finalisées avant le dépôt du dossier d'enquête publique"

Texte: "Le plan de gestion de chantier assure la sécurité, essentielle pour les travaux d'infrastructures"
→ source_object: "Plan de gestion de chantier"
→ target_object: "Travaux d'infrastructures"
→ link_type: "Contribution"
→ justification: "Le plan de gestion de chantier assure la sécurité, essentielle pour les travaux d'infrastructures"

RÉPONSE ATTENDUE:
Format JSON uniquement selon le schéma ALOELinksOutput.
IMPORTANT : Utilise EXACTEMENT les noms de champs suivants :
- "source_object" (pas "source", "objet_source", "from")
- "target_object" (pas "target", "objet_cible", "to", "cible")
- "link_type" (pas "type", "relation", "type_lien")
- "source_attribute" et "target_attribute" (optionnels, laisser vide si non mentionnés)
- "justification"
"""

    links_data = llm.invoke_structured(prompt, ALOELinksOutput)

    page_links_entry = {
        "page_num": current_page["page_num"],
        "links": [link.model_dump() for link in links_data.links]
    }

    return {
        **state,
        "page_aloe_links": state.get("page_aloe_links", []) + [page_links_entry],
        "current_aloe_links_page_index": idx + 1,
        "error_message": None
    }


def should_continue_aloe_links(state: MainState) -> str:
    """Continue ou finish ?"""
    if state.get("current_aloe_links_page_index", 0) >= state["total_pages"]:
        return "finish"
    return "continue"