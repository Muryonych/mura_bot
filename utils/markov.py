import json
import os
import random
import re
from collections import defaultdict

messages_file_path = "mura/messages.json"
rejected_log_path = "mura/rejected_messages.log"

def save_message(peer_id: int, message_text: str):
    from datetime import datetime

    message_text = message_text.strip()
    if (
        not message_text or
        len(message_text.split()) < 2 or
        "http" in message_text or
        message_text.startswith("@") or
        sum(c.isupper() for c in message_text if c.isalpha()) / max(1, sum(c.isalpha() for c in message_text)) > 0.8 or
        re.search(r"(.)\1{4,}", message_text) or
        len(message_text) < 5
    ):
        log_rejected_message(peer_id, message_text)
        return

    if os.path.exists(messages_file_path):
        try:
            with open(messages_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    if not isinstance(data, dict):
        data = {}

    peer_key = str(peer_id)
    if peer_key not in data:
        data[peer_key] = []

    data[peer_key].append({
        "text": message_text,
        "timestamp": datetime.utcnow().isoformat()
    })

    with open(messages_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[MSG] Сохранил сообщение в {peer_key}: {message_text}")

def log_rejected_message(peer_id: int, message_text: str):
    from datetime import datetime
    os.makedirs(os.path.dirname(rejected_log_path), exist_ok=True)
    with open(rejected_log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{datetime.utcnow().isoformat()}] PEER {peer_id} - Отклонено: {message_text}\n")

def load_messages(peer_id: int):
    if not os.path.exists(messages_file_path):
        return []

    try:
        with open(messages_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [m["text"] for m in data.get(str(peer_id), []) if "text" in m]
    except Exception as e:
        print(f"[!] Ошибка загрузки сообщений: {e}")
        return []

def build_markov_chain(messages, order=2):
    chain = defaultdict(list)
    for message in messages:
        words = re.findall(r"\w+|[^\w\s]", message.lower(), re.UNICODE)
        if len(words) < order:
            continue
        for i in range(len(words) - order):
            key = tuple(words[i:i + order])
            next_word = words[i + order]
            chain[key].append(next_word)
    return chain

def is_dull(text):
    words = text.lower().split()
    return len(set(words)) < 3 or len(words) < 5

def spice_up(text):
    import random
    if not text.strip():
        return text

    suffixes = ["😅", "🫠", "лол", "ну ты понял", "ха", "вот так-то"]
    prefixes = ["Ну", "Ээ", "Короче", "Чисто", "Реально", "Бип", "Мяу"]

    if len(text.split()) > 5 and random.random() < 0.5:
        text += " " + random.choice(suffixes)

    if random.random() < 0.3:
        text = random.choice(prefixes) + " " + text

    return text

def generate_message(peer_id: int, max_words=25):
    messages = load_messages(peer_id)
    if not messages:
        return "Недостаточно данных для генерации."

    chain = build_markov_chain(messages)
    if not chain:
        return "Не удалось построить цепочку."

    for _ in range(5):  # до 5 попыток найти нормальный текст
        start_key = random.choice(list(chain.keys()))
        result = list(start_key)

        for _ in range(max_words - len(start_key)):
            next_words = chain.get(tuple(result[-2:]))
            if not next_words:
                break
            result.append(random.choice(next_words))

        generated = " ".join(result).strip()

        if generated and generated[-1] not in ".!?…":
            if random.random() < 0.8:
                generated += random.choice([".", "!", "…"])  # можно разнообразить окончания

        if not is_dull(generated):
            return spice_up(generated)

    return "🤔 не знаю, что и сказать..."

    messages = load_messages(peer_id)
    if not messages:
        return "Недостаточно данных для генерации."

    chain = build_markov_chain(messages)
    if not chain:
        return "Не удалось построить цепочку."

    for _ in range(5):  # до 5 попыток найти нормальный текст
        start_key = random.choice(list(chain.keys()))
        result = list(start_key)

        for _ in range(max_words - len(start_key)):
            next_words = chain.get(tuple(result[-2:]))
            if not next_words:
                break
            result.append(random.choice(next_words))

        generated = " ".join(result).capitalize()
        if generated and generated[-1] not in ".!?":
            generated += "."

        if not is_dull(generated):
            return spice_up(generated)

    return "🤔 не знаю, что и сказать..."
