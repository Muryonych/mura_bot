import json
import os
from datetime import datetime
from collections import defaultdict, Counter
from dateutil import parser as date_parser

CHAT_STATS_PATH = "mura/chat_stats.json"
MESSAGES_PATH = "mura/messages.json"

def save_chat_stats(data):
    with open(CHAT_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def get_chat_title(bot, peer_id: int) -> str:
    try:
        response = await bot.api.messages.get_conversations_by_id(peer_ids=[peer_id])
        if response.items:
            chat = response.items[0].chat_settings
            return chat.title if chat else f"Чат {peer_id}"
    except Exception as e:
        print(f"[!] Не удалось получить название чата {peer_id}: {e}")
    return f"Чат {peer_id}"

async def regenerate_chat_stats_from_messages(bot):
    if not os.path.exists(MESSAGES_PATH):
        print("[!] messages.json не найден.")
        return

    try:
        with open(MESSAGES_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError:
        print("[!] Ошибка чтения messages.json")
        return

    now = datetime.utcnow()
    data = {
        "stats": {
            "total": 0,
            "today": 0,
            "month": 0,
            "last_hour": 0
        },
        "graphs": {
            "hourly": Counter(),
            "daily": defaultdict(lambda: {"total": 0, "hourly": Counter(), "top_chats": Counter()}),
            "top_chats": Counter()
        },
        "chat_titles": {}
    }

    for peer_id, messages in raw_data.items():
        for msg in messages:
            ts = msg.get("timestamp")
            if not ts:
                continue
            try:
                dt = date_parser.parse(ts)
            except Exception:
                continue

            date_str = dt.date().isoformat()
            hour = dt.hour

            data["stats"]["total"] += 1
            data["graphs"]["hourly"][str(hour)] += 1
            data["graphs"]["daily"][date_str]["total"] += 1
            data["graphs"]["daily"][date_str]["hourly"][str(hour)] += 1
            data["graphs"]["daily"][date_str]["top_chats"][peer_id] += 1
            data["graphs"]["top_chats"][peer_id] += 1

            if dt.date() == now.date():
                data["stats"]["today"] += 1
            if dt.year == now.year and dt.month == now.month:
                data["stats"]["month"] += 1
            if (now - dt).total_seconds() < 3600:
                data["stats"]["last_hour"] += 1

        # Добавляем название беседы
        if str(peer_id) not in data["chat_titles"]:
            title = await get_chat_title(bot, int(peer_id))
            data["chat_titles"][str(peer_id)] = {
                "title": title,
                "first_seen": int(datetime.utcnow().timestamp())
            }

    # Финализация
    for day in data["graphs"]["daily"]:
        d = data["graphs"]["daily"][day]
        d["hourly"] = dict(d["hourly"])
        d["top_chats"] = sorted(d["top_chats"].items(), key=lambda x: x[1], reverse=True)[:10]

    data["graphs"]["hourly"] = dict(data["graphs"]["hourly"])
    data["graphs"]["top_chats"] = sorted(data["graphs"]["top_chats"].items(), key=lambda x: x[1], reverse=True)[:10]

    save_chat_stats(data)
    print("[OK] Статистика успешно пересчитана из messages.json")