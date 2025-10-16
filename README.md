# 🧠 MCP Server – FastMCP + Ollama Integration

Questo progetto implementa un **MCP Server** basato su **FastMCP** per consentire a un modello LLM (come Llama 3.2 tramite Ollama) di interagire con risorse, strumenti e prompt personalizzati.  
L’architettura è pensata per gestire pipeline di *Retrieval-Augmented Generation (RAG)* su dati strutturati e schemi FAISS.

---

## 🚀 Avvio rapido

### 1️⃣ Impostare i permessi di esecuzione
Rendi eseguibile lo script di inizializzazione di Ollama:
```bash
chmod +x init_ollama.sh

---

### 2️⃣ Inizializzare Ollama
Esegui lo script per avviare il servizio Ollama e scaricare il modello necessario (ad esempio `llama3.2:3b`):
```bash
./init_ollama.sh

---

### 3️⃣ Avviare il backend MCP
Lancia il container Docker del server FastMCP in modalità detached:
```bash
docker compose up -d backend
