"""
json_memory.py

JSON-backed memory store for user profiles and past drafts.
Supports optional GitHub sync via personal access token.
"""
import json
from pathlib import Path
from typing import Dict, Any
import streamlit as st  # for secrets
from github import Github

MEMORY_PATH = Path(__file__).parent / "user_profiles.json"

# GitHub configuration
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)  # streamlit secrets
REPO_NAME = "mannavapriya/Email-Generator"

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

def upsert_profile(user_id: str, profile: Dict[str, Any], push_to_github: bool = False) -> None:
    """Insert or update profile. Optionally push to GitHub."""
    data = load_profiles()
    data[user_id] = profile
    save_profiles(data)

    if push_to_github and GITHUB_TOKEN:
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(REPO_NAME)
            path_in_repo = str(MEMORY_PATH.relative_to(Path(__file__).parents[1]))
            content = json.dumps(data, indent=2, ensure_ascii=False)

            try:
                # If file exists, update
                contents = repo.get_contents(path_in_repo)
                repo.update_file(contents.path, f"Update {path_in_repo}", content, contents.sha)
            except Exception:
                # If file doesn't exist, create
                repo.create_file(path_in_repo, f"Create {path_in_repo}", content)
        except Exception as e:
            print("GitHub push failed:", e)
