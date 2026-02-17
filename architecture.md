risk_analysis_engine/
│
├── pyproject.toml
├── README.md
│
├── src/
│   └── risk_engine/
│       ├── __init__.py
│       │
│       ├── core/                           # Logique métier pure
│       │   ├── __init__.py
│       │   ├── state.py                    # États globaux et des sous-graphes
│       │   ├── schemas.py                  # Modèles Pydantic
│       │   
│       │
│       ├── nodes/                          # Nœuds atomiques réutilisables
│       │   ├── __init__.py
│       │   ├── extraction.py               # Nœud d'extraction LlamaParse
│       │   ├── human_edit_feedback.py           # Nœuds de validation humaine
│       │   ├── summarization.py            # Nœuds de resumé recursif su rtout le document projet
│       │   ├── risk_detection.py           # Nœuds d'analyse de risques selon le formalisme decidé
│       │   ├── question_answering.py       # Nœuds de Q&A
│       │   └── llm_editor.py                # Responsable de tout ce qui est modification guidée sur les données au cours des differentes étapes 
│       │
│       │   
│       │
│       ├── graphs/                         # Graphe principal
│       │   ├── __init__.py
│       │   └── main_graph.py               # Orchestration complète
│       │
│       ├── services/                       # Services externes
│       │   ├── __init__.py
│       │   ├── llama_parse_client.py       # Client LlamaParse
│       │   └── llm_client.py               # Client LLM (OpenAI, etc.)
│       │
│       ├── storage/                        # Gestion de la mémoire
│       │   ├── __init__.py
│       │   ├── memory.py                   # Mémoire en RAM
│       │   ├── checkpointer.py             # Sauvegarde des états
│       │   └── document_store.py           # Stockage des documents
│       │
│       
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_nodes.py
│   │   └── test_subgraphs.py
│   └── integration/
│       └── test_main_graph.py
│
└── apps/
    ├── streamlit_app.py                    # Interface Streamlit
    └── components/
        ├── sidebar.py                      # Affichage et édition docs
        └── workflow_viz.py                 # Visualisation du workflow