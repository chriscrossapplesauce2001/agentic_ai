# Nemotron Voice Agent — DGX Spark Quickstart

Real-time voice chat with NVIDIA Nemotron on a DGX Spark. Three local models (ASR + LLM + TTS) running on a single GPU with streaming between them — fast enough to feel like a phone call.

## TL;DR

```bash
# 1. Download the LLM (one-time, ~32GB)
hf download unsloth/Nemotron-3-Nano-30B-A3B-GGUF --include "*Q8*"

# 2. Start the backend services
cd ~/cwilsch/agentic_ai/nemotron_voice
./scripts/nemotron.sh start

# 3. Run the voice bot
uv run pipecat_bots/bot_interleaved_streaming.py -t webrtc

# 4. Open http://localhost:7860 in your browser and talk
```

## Prerequisites

- NVIDIA DGX Spark with Docker + NVIDIA Container Toolkit
- Docker image `nemotron-unified:cuda13` already built (see below if not)
- `uv` installed (`pipx install uv`)
- `hf` CLI installed (`pipx install huggingface-hub`)

## Detailed Steps

### One-time setup

**Build the Docker image** (~2-3 hours, only needed once):

```bash
cd ~/cwilsch/agentic_ai/nemotron_voice
docker build -f Dockerfile.unified -t nemotron-unified:cuda13 .
```

**Download the LLM weights** (~32GB, only needed once):

```bash
hf download unsloth/Nemotron-3-Nano-30B-A3B-GGUF --include "*Q8*"
```

**Download the compatible TTS model** (only needed once):

The container's NeMo build requires the January 2026 Magpie TTS model. The latest HuggingFace version added languages the container doesn't support yet.

```bash
hf download nvidia/magpie_tts_multilingual_357m --revision 311be03
```

ASR model (~2.4GB) downloads automatically on first container start.

### Running

**Start the backend** (ASR + TTS + LLM in Docker):

```bash
cd ~/cwilsch/agentic_ai/nemotron_voice
./scripts/nemotron.sh start
```

Check that all services are up:

```bash
./scripts/nemotron.sh status
# Should show ASR, TTS, LLM all UP
```

**Start the voice bot**:

```bash
uv run pipecat_bots/bot_interleaved_streaming.py -t webrtc
```

**Open the UI**: Navigate to `http://localhost:7860` in your browser. Click the microphone and start talking.

### Connecting from another machine (SSH)

If you SSH into the Spark from another computer, forward the ports:

```bash
ssh -L 7860:localhost:7860 -L 8000:localhost:8000 -L 8001:localhost:8001 -L 8080:localhost:8080 agentsmith@192.168.178.106
```

Then open `http://localhost:7860` on your local machine.

### Stopping

```bash
# Stop the voice bot: Ctrl+C in the terminal running it

# Stop the backend services
./scripts/nemotron.sh stop
```

## Services

| Service | Port | What it does |
|---------|------|--------------|
| ASR | 8080 | Speech-to-text (Nemotron Speech, streaming WebSocket) |
| LLM | 8000 | Language model (Nemotron-3-Nano 30B Q8, llama.cpp) |
| TTS | 8001 | Text-to-speech (Magpie TTS, 5 voices) |
| Voice Bot | 7860 | WebRTC UI connecting all three |

## Troubleshooting

**Port already in use**: Something else is on port 8080/8000/8001. Check with `ss -tlnp | grep <port>` and stop the conflicting service (e.g. `docker stop open-webui`).

**TTS crashes on startup**: The Magpie TTS model on HuggingFace was updated in March 2026 with Hindi/Chinese support that the container's NeMo doesn't have. Fix: download the January revision with `hf download nvidia/magpie_tts_multilingual_357m --revision 311be03`. The start script automatically uses this version.

**"No Q8 model found"**: The start script looks in `~/.cache/huggingface/` for the GGUF. If running with `sudo`, pass your home dir: `sudo -E HOME=/home/agentsmith ./scripts/nemotron.sh start`, or specify `--model /full/path/to/Q8_0.gguf`.
