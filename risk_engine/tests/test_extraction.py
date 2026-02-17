# risk_engine/tests/test_extraction.py

import sys
import json
from pathlib import Path
from datetime import datetime

# Remonte de 2 niveaux : tests/ -> risk_engine/ -> racine du projet
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from risk_engine.graphs.main_graph import create_main_graph
from risk_engine.core.state import MainState

# State initial
initial_state = MainState(
    uploaded_file_path=r"C:\Users\beugre niamba\Centrale-sup\risk_modelling_with_GenAI\data\10.-2.-BCCOHP-Quality-Assurance-Program-Project-Complex-Project-Charter.pdf",
    file_name="10.-2.-BCCOHP-Quality-Assurance-Program-Project-Complex-Project-Charter.pdf",
    file_type="pdf",
    upload_status="pending",
    extraction_status="pending",
    pages=[],
    total_pages=0,
    raw_text="",
    extraction_time=0.0,
    error_message=None
)

# Lance le graphe
graph = create_main_graph()
result = graph.invoke(initial_state)

# Affiche résultats
print(f"\n{'='*50}")
print(f" RÉSULTATS EXTRACTION")
print(f"{'='*50}")
print(f"Status: {result['extraction_status']}")
print(f"Total pages: {result['total_pages']}")
print(f"Temps: {result['extraction_time']:.2f}s")

if result['pages']:
    print(f"\n PAGE 1:")
    page1 = result['pages'][0]
    print(f"Content preview: {page1['content'][:300]}...")


output_dir = project_root / "data" / "extraction_results"
output_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = output_dir / f"extraction_{timestamp}.json"


with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\ Résultat sauvegardé : {output_file}")