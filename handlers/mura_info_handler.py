from vkbottle.bot import Message, BotLabeler
from utils.chat_settings import get_chat_setting
import json
import os

labeler = BotLabeler()
labeler.vbml_ignore_case = True

@labeler.message(text=["мура инфо", "мура информация", "mura info"])
async def mura_info_handler(message: Message):
    peer_id = str(message.peer_id)

    # Шанс ответа из настроек
    chance = get_chat_setting(peer_id, "mura_chance", 0)

    # Путь к статистике
    stats_file = "mura/chat_stats.json"
    message_count = 0

    if os.path.exists(stats_file):
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)
            top_chats = stats.get("graphs", {}).get("top_chats", [])
            for chat_id, count in top_chats:
                if chat_id == peer_id:
                    message_count = count
                    break

    text = (
        "🤖 Информация о работе Муры в этой беседе:\n\n"
        f"🔁 Шанс ответа: {chance}%\n"
        f"💬 Всего сообщений в базе: {message_count}"
    )

    await message.answer(text)
