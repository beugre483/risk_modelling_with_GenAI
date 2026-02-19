# test_graph_visualization.py

from risk_engine.graphs.main_graph import create_main_graph
from IPython.display import Image, display

# Crée le graphe
graph = create_main_graph()

# Génère l'image
img = graph.get_graph().draw_mermaid_png()

# Sauvegarde
with open("graph_visualization.png", "wb") as f:
    f.write(img)

print("✅ Graphe sauvegardé dans graph_visualization.png")