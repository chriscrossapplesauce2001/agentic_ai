#!/usr/bin/env bash
# voice_chat/start.sh — Start local voice chat with Nemotron 3 Nano 4B + Open WebUI
set -euo pipefail

MODEL="hf.co/unsloth/NVIDIA-Nemotron-3-Nano-4B-GGUF:Q8_0"

# 1. Ensure Ollama is running
if ! pgrep -x ollama >/dev/null 2>&1; then
  echo "Starting Ollama..."
  ollama serve &
  sleep 3
fi

# 2. Pull model if not present
if ! ollama list | grep -q "$MODEL"; then
  echo "Pulling $MODEL ..."
  ollama pull "$MODEL"
fi

# 3. Start Open WebUI (skip if already running)
if docker ps --format '{{.Names}}' | grep -q '^open-webui$'; then
  echo "Open WebUI is already running."
elif docker ps -a --format '{{.Names}}' | grep -q '^open-webui$'; then
  echo "Restarting stopped Open WebUI container..."
  docker start open-webui
else
  echo "Starting Open WebUI (CUDA) ..."
  docker run -d --gpus all --network=host \
    -v open-webui:/app/backend/data \
    --name open-webui \
    ghcr.io/open-webui/open-webui:cuda
fi

# 4. Wait for Open WebUI to be ready
echo "Waiting for Open WebUI to start..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8080/api/version >/dev/null 2>&1; then
    echo "Open WebUI is ready!"
    break
  fi
  sleep 2
done

# 5. Print access info
echo ""
echo "========================================="
echo "  Voice Chat is ready!"
echo "  Open: http://localhost:8080"
echo "  Model: $MODEL"
echo "========================================="
echo ""
echo "To enable voice chat: Click the microphone icon in the chat"
echo "input bar. Grant browser mic permissions when prompted."
