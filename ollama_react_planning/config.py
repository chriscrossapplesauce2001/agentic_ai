import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _load():
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


_cfg = _load()

MODEL              = _cfg.get("model", "qwen3:0.6b")
NUM_CTX            = _cfg.get("num_ctx", 4096)
TEMPERATURE        = _cfg.get("temperature", 0.7)
MAX_PAOR_CYCLES    = _cfg.get("max_paor_cycles", 10)
MAX_PLAN_STEPS     = _cfg.get("max_plan_steps", 5)
SEARCH_MAX_RESULTS = _cfg.get("search_max_results", 4)
SYSTEM_PROMPT      = _cfg.get("system_prompt", "You are a helpful assistant.")
DEMO_QUERIES       = _cfg.get("demo_queries", [])
