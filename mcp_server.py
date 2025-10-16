import asyncio
import json
import logging
import requests
import os
from typing import Any
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from pipeline import init_pipeline
from search_schema import search

from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import torch
import ollama

logging.basicConfig(level=logging.INFO)

# Avvio MCP server
mcp = FastMCP("schema_rag_server")

# Output model (opzionale, per chiarezza)
class SearchOutput(BaseModel):
    query: str
    results: list[dict]

def query_llama(prompt: str) -> str:
    response = requests.post(
        "http://ollama:11434/api/generate",
        json={"model": "llama3.2:3b", "prompt": prompt, "stream": True},
        stream=True,
        timeout=120
    )

    output_chunks = []
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            logging.info(f"[Ollama RAW CHUNK] {data}")
            if "response" in data:
                output_chunks.append(data["response"])

    full_output = "".join(output_chunks).strip()
    logging.info(f"[Ollama RAW OUTPUT]\n{full_output if full_output else '[VUOTO]'}")
    return full_output

# Tool MCP: ricerca schema
@mcp.tool()
def search_schema(query: str, top_k: int = 3) -> str:
    try:
        logging.info(f"[MCP] Nuova query: {query}")
        results = search(query, top_k=top_k)
        return json.dumps(SearchOutput(query=query, results=results).dict(), indent=2, ensure_ascii=False)
    except Exception as e:
        logging.exception("[MCP] Errore in search_schema")
        return json.dumps({"error": str(e)})

# Tool MCP: generazione SQL con SQLCoder + schema FAISS
@mcp.tool()
def text_to_sql(message: str, top_k: int = 3) -> str:
    """
    Usa il modello defog/sqlcoder-7b-2 per tradurre una richiesta in linguaggio naturale in SQL,
    includendo nel prompt lo schema recuperato da FAISS.
    """
    try:
        # 1. Recupero schema rilevante
        results = search(message, top_k=top_k)  # funzione dal tuo search_schema.py
        schema_str = "\n".join(
            f"Table: {r['table_name']}, Description: {r['description']}, Fields: " +
            ", ".join(f.get("description","") for f in r["fields"] if f.get("description"))
            for r in results
        )

        # 2. Creo il prompt con schema + domanda
        prompt = f"""
        Sei un assistente SQL.
        Genera SOLO una query SQL valida e ottimizzata che risponda alla richiesta dell'utente.
        ⚠️ Non aggiungere testo, spiegazioni o commenti.
        Usa SOLO le seguenti tabelle e campi:
        
        {schema_str}
        
        Domanda utente:
        {message}
        
        Output atteso: SOLO SQL, senza testo extra.
        """

        sql = query_llama(prompt)

        return json.dumps({"input": message, "schema": results, "sql": sql},
                          indent=2, ensure_ascii=False)

    except Exception as e:
        logging.exception("[MCP] Errore in text_to_sql")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    init_pipeline()

    # Query di test
    query = "Mostrami il fatturato del 2022"

    # Chiamata diretta a search_schema
    res1 = search_schema(query, top_k=3)
    print("🔎 Risultato search_schema():")
    print(res1)

    # Chiamata diretta a text_to_sql
    res2 = text_to_sql(query, top_k=3)
    print("🧠 Risultato text_to_sql():")
    print(res2)

    # Avvia MCP server
    mcp.run()

# Per far partire tutto:
# chmod +x init_ollama.sh
# ./init_ollama.sh
# docker compose up -d backend