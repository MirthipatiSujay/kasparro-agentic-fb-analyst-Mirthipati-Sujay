import json
import traceback
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("logs/agent_log.jsonl")

def _ensure_log_dir():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_event(agent: str,
              stage: str,
              level: str = "info",
              message: str = "",
              **extra):
    """
    Structured JSON log line:
    {
      "timestamp": "...Z",
      "agent": "DataAgent",
      "stage": "load_data",
      "level": "info|error|debug",
      "message": "Loaded dataset",
      "extra": { ... }
    }
    """
    _ensure_log_dir()
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "stage": stage,
        "level": level,
        "message": message,
        "extra": extra,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def log_error(agent: str, stage: str, message: str, exc: Exception):
    log_event(
        agent=agent,
        stage=stage,
        level="error",
        message=message,
        traceback=traceback.format_exc(),
        error_type=type(exc).__name__,
    )
