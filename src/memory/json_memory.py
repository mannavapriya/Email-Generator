"""
json_memory.py

Simple JSON-backed memory store for user profiles and past drafts.
"""
import json
from pathlib import Path
from typing import Dict, Any

MEMORY_PATH = Path(__file__).parent / "user_profiles.json"

def load_profiles() -> Dict[str, Any]:
    if not MEMORY_PATH.exists():
        return {}
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(data: Dict[str, Any]) -> None:
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_profile(user_id: str = "default") -> Dict[str, Any]:
    data = load_profiles()
    return data.get(user_id, {})

def upsert_profile(user_id: str, profile: Dict[str, Any]) -> None:
    data = load_profiles()
    data[user_id] = profile
    save_profiles(data)
