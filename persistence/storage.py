import json
import os
from typing import Any, Dict

from config import SAVE_PATH


def default_state() -> Dict[str, Any]:
    return {"corruption": 0.0, "level": 1}


def load_state() -> Dict[str, Any]:
    if not os.path.isfile(SAVE_PATH):
        return default_state()
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = default_state()
        out.update({k: data[k] for k in out if k in data})
        return out
    except (OSError, json.JSONDecodeError):
        return default_state()


def save_state(corruption_level: float, level_id: int) -> None:
    payload = {"corruption": float(corruption_level), "level": int(level_id)}
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass
