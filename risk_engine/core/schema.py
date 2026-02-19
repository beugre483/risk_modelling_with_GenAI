# core/schemas.py

from pydantic import BaseModel, Field


class SummaryOutput(BaseModel):
    """
    Sortie structurée du LLM pour le résumé d'une page
    """
    page_summary: str = Field(
        ...,
        description="Résumé de la page actuelle uniquement, sans référence aux pages précédentes. Doit capturer les points clés, décisions importantes et informations essentielles de cette page."
    )
    
    global_summary: str = Field(
        ...,
        description="Résumé cumulatif mis à jour intégrant toutes les pages vues jusqu'ici (page 1 à page N). Doit maintenir la cohérence narrative et inclure les éléments importants de toutes les pages précédentes plus la page actuelle."
    )
    
    
    # core/schemas.py

from pydantic import BaseModel, Field
from typing import List


class VulnerableElement(BaseModel):
    """Élément vulnérable identifié"""
    element: str = Field(
        ...,
        description="Nom synthétique de l'élément vulnérable (ressource, activité, contrainte, installation)"
    )
    justification: str = Field(
        ...,
        description="Extrait ou paraphrase du document expliquant pourquoi cet élément est fragile/vulnérable"
    )


class ThreatAssociation(BaseModel):
    """Menace associée à un élément vulnérable"""
    vulnerable_element: str = Field(
        ...,
        description="Nom de l'élément vulnérable concerné"
    )
    threat: str = Field(
        ...,
        description="Description claire de la menace (facteur externe ou interne)"
    )
    justification: str = Field(
        ...,
        description="Lien logique entre la menace et la vulnérabilité"
    )
    potential_impact: str = Field(
        ...,
        description="Impact sur les objectifs du projet (délai, coût, qualité)"
    )


class RiskAnalysisOutput(BaseModel):
    """Sortie de l'analyse de risques pour une page"""
    vulnerable_elements: List[VulnerableElement] = Field(
        default_factory=list,
        description="Liste des éléments vulnérables identifiés dans cette page"
    )
    threat_associations: List[ThreatAssociation] = Field(
        default_factory=list,
        description="Liste des menaces associées aux éléments vulnérables"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "vulnerable_elements": [
                    {
                        "element": "Budget de finition trop serré",
                        "justification": "Le budget alloué aux finitions représente seulement 5% du coût total, limitant la flexibilité en cas de hausse des prix"
                    }
                ],
                "threat_associations": [
                    {
                        "vulnerable_element": "Budget de finition trop serré",
                        "threat": "Dépassement des coûts de matériaux",
                        "justification": "Une inflation de 10% sur les peintures épuisera la ligne budgétaire",
                        "potential_impact": "Arbitrages dégradant la qualité du projet"
                    }
                ]
            }
        }
    
