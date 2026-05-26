import json
import os
from typing import Any, Dict

from config import SAVE_PATH, CONFIG_PATH, WIDTH, HEIGHT, LIMIT_FPS


def default_state() -> Dict[str, Any]:
    return {"corruption": 0.0, "level": 1, "max_level": 1}


def default_settings() -> Dict[str, Any]:
    return {"width": WIDTH, "height": HEIGHT, "limit_fps": LIMIT_FPS}


def load_state() -> Dict[str, Any]:
    if not os.path.isfile(SAVE_PATH):
        return default_state()
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = default_state()
        # Carrega campos existentes preservando tipos
        for k in out:
            if k in data:
                out[k] = data[k]
        return out
    except (OSError, json.JSONDecodeError):
        return default_state()


def load_settings() -> Dict[str, Any]:
    if not os.path.isfile(CONFIG_PATH):
        return default_settings()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        out = default_settings()
        out.update(data)
        return out
    except (OSError, json.JSONDecodeError):
        return default_settings()


def save_state(corruption_level: float, level_id: int, max_level: int = 1) -> None:
    payload = {
        "corruption": float(corruption_level),
        "level": int(level_id),
        "max_level": int(max_level)
    }
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass


def save_settings(width: int, height: int, limit_fps: bool) -> None:
    payload = {"width": width, "height": height, "limit_fps": limit_fps}
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except OSError:
        pass
