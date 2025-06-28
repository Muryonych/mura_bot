import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from vkbottle.bot import Message, BotLabeler
from utils.reply_filter import should_reply
from utils.markov import generate_message, save_message, load_messages  # Импортируем функцию load_messages
from utils.chat_stats import record_chat_message
from utils.chat_settings import get_chat_setting
from handlers.reputation_handler import update_reputation  # ✅ Добавлено

labeler = BotLabeler()
labeler.vbml_ignore_case = True


# Функция для проверки, прошло ли достаточно времени с последнего сообщения
def can_send_message(peer_id: int, time_limit=10):
    messages = load_messages(peer_id)  # Загружаем все сообщения для данной беседы
    if not messages:
        return True  # Если сообщений нет, разрешаем отправить

    # Проверка на то, что messages - это список словарей
    if isinstance(messages, list) and isinstance(messages[-1], dict):
        # Получаем время последнего сообщения
        last_message = messages[-1]
        last_timestamp = last_message.get("timestamp")
        if last_timestamp is None:
            return True  # Если нет временной метки, разрешаем отправить

        last_time = datetime.fromisoformat(last_timestamp)

        # Проверяем, прошло ли достаточно времени
        time_diff = datetime.utcnow() - last_time
        if time_diff.total_seconds() < time_limit:
            print(f"[TIMEOUT] Для беседы {peer_id} не прошло 10 секунд с последнего сообщения.")
            return False  # Если прошло меньше, чем time_limit, не отправляем сообщение

    return True  # Если прошло достаточно времени, разрешаем отправить


@labeler.message(text=["мура пинг", "Мура пинг", "МУРА ПИНГ"])
async def ping_command(message: Message):
    await message.answer("Понг")


@labeler.message(text=["мура анекдот", "Мура анекдот", "МУРА АНЕКДОТ"])
async def joke_command(message: Message):
    url = "https://www.anekdot.ru/random/anekdot/"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find("div", class_="text")
        if not tag or not tag.text.strip():
            await message.answer("Не удалось найти анекдот 😢")
            return
        joke = tag.text.strip()
        await message.answer(joke)
    except Exception:
        await message.answer("Ошибка при получении анекдота.")


@labeler.message()
async def markov_listener(message: Message):
    # Не отвечаем в ЛС
    if message.peer_id < 2000000000:
        return

    # Игнорируем сообщения от ботов и сообществ
    if message.from_id < 0:
        return

    lower_text = (message.text or "").lower()
    if lower_text.startswith(("мура мем", "мура пинг", "мура анекдот", "мура шанс")):
        return

    if message.text:
        # Пропускаем обработку, если не прошло достаточно времени
        if not can_send_message(message.peer_id, time_limit=10):
            await message.answer("Подожди 10 секунд перед следующим сообщением.")
            return

        # Обновляем репутацию
        await update_reputation(message.peer_id, message.from_id, message.text, message.ctx_api)

        # Сохраняем сообщение в messages.json
        save_message(peer_id=message.peer_id, message_text=message.text)

        # Обновляем статистику
        try:
            chat_title = None
            if hasattr(message, "chat") and message.chat and getattr(message.chat, "title", None):
                chat_title = message.chat.title

            record_chat_message(
                peer_id=str(message.peer_id),
                timestamp=datetime.utcnow(),
                chat_title=chat_title
            )
            print(f"[STATS] Обновил статистику для {message.peer_id}: {message.text}")
        except Exception as e:
            print(f"[!] Ошибка обновления статистики: {e}")

        # Получаем шанс генерации (по умолчанию 100%)
        chance = get_chat_setting(str(message.peer_id), "mura_chance")
        if chance is None:
            chance = 50

        if random.randint(1, 100) <= chance:
            reply = generate_message(peer_id=message.peer_id)
            if reply:
                await message.answer(reply)
