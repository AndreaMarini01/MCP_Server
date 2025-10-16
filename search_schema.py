import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL = "intfloat/e5-large"
encoder = SentenceTransformer(MODEL)

def search(query, index_file="schema.index", mapping_file="schema_mapping.json", top_k=3, output_file="search_results.json"):
    index = faiss.read_index(index_file)
    with open(mapping_file, "r") as f:
        mapping = json.load(f)

    q_emb = encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, ids = index.search(q_emb, top_k)

    results = []

    # Struttura per debug (con embedding query e tabelle)
    debug_results = {
        "query": query,
        "query_embedding": q_emb[0].tolist(),
        "matches": []
    }

    for score, idx in zip(scores[0], ids[0]):
        table = mapping[str(idx)]
        results.append({
            "score": float(score),
            "table_name": table["table_name"],
            "description": table["description"],
            "fields": table["fields"]
        })

        text = f"Description: {table['description']}. Fields: " + \
               ", ".join([f.get('description','') for f in table['fields'] if f.get('description')])
        table_emb = encoder.encode([text], convert_to_numpy=True, normalize_embeddings=True)[0].tolist()


        debug_results["matches"].append({
            "score": float(score),
            "table_name": table["table_name"],
            "description": table["description"],
            "embedding": table_emb
        })

    # Salva su file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

        # Salva file di debug con embedding
    with open("search_debug.json", "w") as f:
        json.dump(debug_results, f, indent=2, ensure_ascii=False)


    print(f"✅ Risultati salvati in {output_file}")
    print("🔎 File di debug salvato in search_debug.json")
    return results
