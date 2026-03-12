# core/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from typing import Literal

from enum import Enum


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
        use_enum_values =True
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
    



class ObjectCategory(str, Enum):
    """Catégories d'objets ALOE"""
    OBJECTIF = "Objectif"
    ACTIVITE = "Activité/Processus"
    ORGANISATION = "Organisation/Acteur"
    RESSOURCE = "Ressource"
    LIVRABLE = "Livrable/Produit"


class AttributeName(str, Enum):
    """Attributs ALOE"""
    COUT = "Coût"
    DUREE = "Durée"
    QUALITE = "Qualité"
    DATE = "Date"
    AVANCEMENT = "Avancement"
    DESCRIPTION = "Description"
    RESSOURCES = "Ressources allouées"
    VALEUR = "Valeur ajoutée"


class Attribute(BaseModel):
    """Attribut d'un objet ALOE"""
    name: AttributeName = Field(..., description="Nom de l'attribut")
    value: Optional[str] = Field(None, description="Valeur mentionnée (ex: '500K€', '6 mois')")
    justification: str = Field(..., description="Citation du document")


from pydantic import BaseModel, Field, model_validator
from typing import Any

class ALOEObject(BaseModel):
    object_name: str = Field(..., description="Nom de l'objet (ex: 'Budget finition')")
    category: ObjectCategory = Field(..., description="Catégorie ALOE")
    attributes: List[Attribute] = Field(..., description="Attributs de l'objet")
    justification: str = Field(..., description="Citation du document")

    @model_validator(mode="before")
    @classmethod
    def normalize_field_names(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Rattrape toutes les variantes que le LLM peut générer
            aliases = [
                "objectif_name", "activite_name", "ressource_name",
                "livrable_name", "organisation_name", "name", "nom"
            ]
            if "object_name" not in values or not values["object_name"]:
                for alias in aliases:
                    if alias in values and values[alias]:
                        values["object_name"] = values[alias]
                        break
        return values


class ALOEOutput(BaseModel):
    """Sortie extraction ALOE"""
    objects: List[ALOEObject] = Field(default_factory=list, description="Objets ALOE extraits")
    
    
class VulnerableALOEElement(BaseModel):
    """Élément vulnérable ALOE identifié"""
    aloe_object_name: str = Field(..., description="Nom de l'objet ALOE vulnérable")
    vulnerable_attribute: str = Field(..., description="Attribut ALOE vulnérable")
    threat: str = Field(..., description="Menace identifiée")
    propagation_path: Optional[str] = Field(
        None,
        description="Chemin de propagation via les liens (ex: 'Objet1 → Objet2 (Séquentiel)')"
    )
    justification: str = Field(..., description="Justification de la vulnérabilité")


class ALOEVulnerabilityOutput(BaseModel):
    """Sortie : vulnérabilités ALOE"""
    vulnerable_elements: List[VulnerableALOEElement] = Field(
        default_factory=list,
        description="Éléments vulnérables identifiés"
    )
    
    class Config:
        use_enum_values = True
        
        
class ALOELink(BaseModel):
    """Lien entre deux objets ALOE"""
    link_type: Literal["Contribution", "Séquentiel", "Influence", "Échange"] = Field(
        ...,
        description="Type de lien entre les objets"
    )
    object_1: str = Field(..., description="Nom du premier objet ALOE")
    object_2: str = Field(..., description="Nom du second objet ALOE")
    justification: str = Field(..., description="Explication du lien basée sur le contexte")


class ALOELinksOutput(BaseModel):
    """Sortie : liens entre objets ALOE"""
    links: List[ALOELink] = Field(default_factory=list, description="Liens identifiés")
    
    class Config:
        use_enum_values = True