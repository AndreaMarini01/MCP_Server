#!/bin/sh
set -e

MODEL_NAME="llama3.2:3b"

echo "🚀 Avvio Ollama in background..."
docker compose up -d ollama

echo "⏳ Controllo se il modello $MODEL_NAME è già presente..."
if docker exec ollama ollama show "$MODEL_NAME" >/dev/null 2>&1; then
  echo "✅ Modello $MODEL_NAME già installato."
else
  echo "⬇️  Scarico il modello $MODEL_NAME..."
  docker exec -it ollama ollama pull "$MODEL_NAME"
  echo "✅ Modello $MODEL_NAME installato."
fi

echo "⚡ Ollama è pronto con il modello $MODEL_NAME."