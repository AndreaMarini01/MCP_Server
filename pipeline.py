import os
import subprocess
from search_schema import search  # la funzione che fa embedding query + retrieval

def init_pipeline():
    """Eseguito solo una volta, prepara i file costanti"""
    if not os.path.exists("schema_reduced.json"):
        print("⚙️ Parsing documentazione...")
        subprocess.run(["python", "schema_tabellare.py"], check=True)

    if not (os.path.exists("schema.index") and os.path.exists("schema_mapping.json")):
        print("⚙️ Costruzione embedding tabelle...")
        subprocess.run(["python", "build_index.py"], check=True)

if __name__ == "__main__":
    init_pipeline()
