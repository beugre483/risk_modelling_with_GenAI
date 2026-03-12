# nodes/aloe_extraction.py

from ..core.state import MainState
from ..core.schema import ALOEOutput
from ..services.llm_client import get_llm
from typing import Dict


def extract_aloe_objects_node(state: MainState) -> Dict:
    """
    Extrait les objets ALOE et leurs attributs page par page
    """
    idx = state.get("current_aloe_page_index", 0)
    
    if idx >= state["total_pages"]:
        return {**state}
    
    current_page = state["pages"][idx]
    current_page_summary = state["page_summaries"][idx]["summary"]
    
    last_page_summary = ""
    if idx > 0:
        last_page_summary = state["page_summaries"][idx - 1]["summary"]
    
    already_extracted = "\n".join([
        f"- {obj}" for obj in state.get("all_extracted_aloe_objects", [])
    ])
    
    llm = get_llm()
    
    prompt = f"""Vous êtes un spécialiste de la méthode ALOE, une approche structurée d'analyse des risques dans des projets complexes.

CONTEXTE - Analyse page par page:

PAGE EN COURS: {current_page['page_num']} sur {state['total_pages']}

DONNEES DISPONIBLES:

1. RESUME GLOBAL (pages 1 à {idx}):
{state.get('global_summary', 'Première page - pas de contexte antérieur')}

2. RESUME PAGE PRECEDENTE (page {idx}):
{last_page_summary if last_page_summary else 'Aucune page précédente'}

3. RESUME PAGE ACTUELLE (page {current_page['page_num']}):
{current_page_summary}

4. CONTENU COMPLET PAGE ACTUELLE:
{current_page['content']}

5. OBJETS ALOE DEJA EXTRAITS (ne PAS répéter):
{already_extracted if already_extracted else 'Aucun objet extrait précédemment'}

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

VOTRE MISSION:

Extraire de la page actuelle tous les OBJETS ALOE mentionnés avec leurs ATTRIBUTS.

Pour chaque objet identifié:
1. Donnez-lui un nom concret et spécifique
2. Classez-le dans une des 5 catégories ALOE
3. Identifiez ses attributs mentionnés dans le document avec leurs valeurs
4. Justifiez par des citations du document

REGLES STRICTES:

- Extraire UNIQUEMENT des objets concrets mentionnés dans le document
- Ne PAS répéter les objets déjà dans la liste "OBJETS ALOE DEJA EXTRAITS"
- Chaque objet doit avoir AU MOINS 1 attribut
- Toute extraction doit être justifiée par une citation du document
- Rester factuel, ne pas interpréter au-delà du contenu

EXEMPLES D'EXTRACTION:

Texte: "Le budget alloué aux finitions représente seulement 5% du coût total du projet"

Extraction correcte:
- Objet: "Budget de finition"
- Catégorie: Ressource
- Attributs:
  * Coût: "5% du coût total"
  * Qualité: mention de contrainte budgétaire
- Justification: "Le budget alloué aux finitions représente seulement 5% du coût total du projet"

Texte: "L'activité de terrassement a démarré 3 mois avant l'obtention des permis"

Extraction correcte:
- Objet: "Activité de terrassement"
- Catégorie: Activité/Processus
- Attributs:
  * Date de début/fin: "3 mois avant permis"
  * Avancement: démarrage anticipé
- Justification: "L'activité de terrassement a démarré 3 mois avant l'obtention des permis"

IMPORTANT:
Travaillez page par page, en évitant les redites, pour construire une extraction cumulative, progressive et exhaustive des objets ALOE du projet.

REPONSE ATTENDUE:
Format JSON uniquement selon le schéma ALOEOutput.
IMPORTANT : Le champ doit s'appeler EXACTEMENT "object_name" (pas "objectif_name", 
pas "activite_name", pas "nom"). Respecte scrupuleusement le schéma JSON fourni.

"""
    
    aloe_data = llm.invoke_structured(prompt, ALOEOutput)
    
    new_objects = [obj.object_name for obj in aloe_data.objects]
    
    page_aloe_entry = {
        "page_num": current_page["page_num"],
        "aloe_objects": [obj.model_dump() for obj in aloe_data.objects]
    }
    
    return {
        **state,
        "page_aloe_objects": state.get("page_aloe_objects", []) + [page_aloe_entry],
        "all_extracted_aloe_objects": state.get("all_extracted_aloe_objects", []) + new_objects,
        "current_aloe_page_index": idx + 1,
        "error_message": None
    }


def should_continue_aloe_extraction(state: MainState) -> str:
    """Continue ou fini ?"""
    if state.get("current_aloe_page_index", 0) >= state["total_pages"]:
        return "finish"
    return "continue"