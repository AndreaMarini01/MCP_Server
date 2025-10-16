import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL = "intfloat/e5-large"  # embedding compatto e veloce
encoder = SentenceTransformer(MODEL)

def build_index(schema_file="schema_reduced.json", index_file="schema.index", mapping_file="schema_mapping.json"):
    with open(schema_file, "r") as f:
        tables = json.load(f)

    docs = []
    mapping = {}
    for i, table in enumerate(tables):
        # testo che rappresenta la tabella che verrà poi embeddato
        # build_index.py
        text = f"Description: {table['description']}. Fields: " + \
               ", ".join([f.get('description','') for f in table['fields'] if f.get('description')])

        docs.append(text)
        mapping[i] = table  # mappa ID FAISS → tabella completa

    # embeddings
    embeddings = encoder.encode(docs, convert_to_numpy=True, normalize_embeddings=True)

    # crea index FAISS
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product (cosine)
    index.add(embeddings)

    faiss.write_index(index, index_file)
    with open(mapping_file, "w") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"✅ Indice costruito con {len(tables)} tabelle")

if __name__ == "__main__":
    build_index()
