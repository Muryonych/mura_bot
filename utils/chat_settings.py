import json
import os

# Абсолютный путь к файлу chat_settings.json в папке mura/mura
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "mura", "chat_settings.json")
SETTINGS_FILE = os.path.abspath(SETTINGS_FILE)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def set_chat_setting(peer_id: str, key: str, value):
    settings = load_settings()
    if peer_id not in settings:
        settings[peer_id] = {}
    settings[peer_id][key] = value
    save_settings(settings)

def get_chat_setting(peer_id: str, key: str, default=None):
    settings = load_settings()
    return settings.get(peer_id, {}).get(key, default)
