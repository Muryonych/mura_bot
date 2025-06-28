import json
import os
from datetime import datetime

CHAT_STATS_PATH = "mura/chat_stats.json"

def load_chat_stats():
    # Если нет файла — создаём пустую структуру
    if not os.path.exists(CHAT_STATS_PATH):
        return {
            "stats": {"total": 0, "today": 0, "month": 0, "last_hour": 0},
            "graphs": {"hourly": {}, "daily": {}, "top_chats": {}},
            "chat_titles": {}
        }
    # Иначе читаем и сразу нормализуем все top_chats в словари
    with open(CHAT_STATS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Нормализуем глобальные top_chats
    tc = raw.get("graphs", {}).get("top_chats", [])
    if isinstance(tc, list):
        raw["graphs"]["top_chats"] = {str(k): v for k, v in tc if isinstance(k, (str, int)) and isinstance(v, int)}
    # Нормализуем daily top_chats
    daily = raw["graphs"].get("daily", {})
    for day, bucket in daily.items():
        dtc = bucket.get("top_chats", [])
        if isinstance(dtc, list):
            bucket["top_chats"] = {str(k): v for k, v in dtc if isinstance(k, (str, int)) and isinstance(v, int)}
    return raw

def save_chat_stats(data):
    # При сохранении превращаем оба словаря top_chats обратно в списки пар
    data["graphs"]["top_chats"] = list(data["graphs"]["top_chats"].items())
    for day, bucket in data["graphs"]["daily"].items():
        bucket["top_chats"] = list(bucket["top_chats"].items())
    with open(CHAT_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def record_chat_message(peer_id: str, timestamp: datetime, chat_title: str = None):
    data = load_chat_stats()
    now = datetime.utcnow()

    # --- обновляем stats ---
    data["stats"]["total"] += 1
    if timestamp.date() == now.date():
        data["stats"]["today"] += 1
    if timestamp.year == now.year and timestamp.month == now.month:
        data["stats"]["month"] += 1
    if (now - timestamp).total_seconds() < 3600:
        data["stats"]["last_hour"] += 1

    # --- hourly ---
    hr = str(timestamp.hour)
    data["graphs"]["hourly"][hr] = data["graphs"]["hourly"].get(hr, 0) + 1

    # --- daily ---
    day = timestamp.date().isoformat()
    if day not in data["graphs"]["daily"]:
        data["graphs"]["daily"][day] = {"total": 0, "hourly": {}, "top_chats": {}}
    bucket = data["graphs"]["daily"][day]
    bucket["total"] += 1
    bucket["hourly"][hr] = bucket["hourly"].get(hr, 0) + 1
    bucket["top_chats"][peer_id] = bucket["top_chats"].get(peer_id, 0) + 1

    # --- global top_chats ---
    gtc = data["graphs"]["top_chats"]
    gtc[peer_id] = gtc.get(peer_id, 0) + 1

    # --- сохраняем title ---
    if chat_title:
        data.setdefault("chat_titles", {})
        if peer_id not in data["chat_titles"]:
            data["chat_titles"][peer_id] = {"title": chat_title, "first_seen": int(timestamp.timestamp())}

    save_chat_stats(data)
