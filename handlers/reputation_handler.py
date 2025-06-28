import json
import os
import re
from vkbottle.bot import Message, BotLabeler
from vkbottle import VKAPIError

labeler = BotLabeler()
labeler.vbml_ignore_case = True

REPUTATION_FILE = "mura/reputation.json"
os.makedirs("mura", exist_ok=True)

# 🔐 Укажи свой VK ID:
ADMIN_USER_ID = 561153765  # ← ЗАМЕНИ на свой ID!

# 👑 Ранги и их границы
RANKS = [
    (1500, "👑 Легенда"),
    (800, "🦸 Герой"),
    (400, "🛡 Ветеран"),
    (200, "💬 Активист"),
    (10, "👤 Участник"),
    (0, "🐣 Новичок"),
]


def get_rank(score: int) -> str:
    for threshold, name in RANKS:
        if score >= threshold:
            return name
    return "❓ Неизвестный"


def load_reputation():
    if not os.path.exists(REPUTATION_FILE):
        return {}
    with open(REPUTATION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_reputation(data):
    with open(REPUTATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def update_reputation(peer_id, user_id, message_text, ctx_api):
    if len(message_text) < 5:
        return

    # Проверка на живого пользователя
    try:
        user = await ctx_api.users.get(user_ids=[user_id])
        if user[0].is_closed is None:
            return  # Не пользователь (бот/группа)
    except VKAPIError:
        return

    data = load_reputation()
    peer_id = str(peer_id)
    user_id = str(user_id)

    if peer_id not in data:
        data[peer_id] = {}

    data[peer_id][user_id] = data[peer_id].get(user_id, 0) + 1
    save_reputation(data)


def get_user_reputation(peer_id, user_id):
    data = load_reputation()
    return data.get(str(peer_id), {}).get(str(user_id), 0)


async def get_top_users(peer_id, ctx_api, top_n=10):
    data = load_reputation()
    peer_data = data.get(str(peer_id), {})

    sorted_users = sorted(peer_data.items(), key=lambda x: x[1], reverse=True)

    real_users = []
    for uid, score in sorted_users:
        try:
            user = await ctx_api.users.get(user_ids=[uid])
            if user and user[0].is_closed is not None:
                real_users.append((uid, score))
        except Exception:
            continue

        if len(real_users) >= top_n:
            break

    return real_users


def extract_user_id(query):
    match = re.search(r"(?:id|club)?(\d+)", query)
    return int(match.group(1)) if match else None


@labeler.message(text=["мура топ", "Мура топ", "МУРА ТОП"])
async def top_command(message: Message):
    peer_id = message.peer_id
    top_users = await get_top_users(peer_id, message.ctx_api)

    if not top_users:
        await message.answer("В чате пока нет репутации.")
        return

    lines = []
    user_ids = [int(uid) for uid, _ in top_users]

    try:
        users_info = await message.ctx_api.users.get(user_ids=user_ids)
        user_map = {str(user.id): f"{user.first_name} {user.last_name}" for user in users_info}
    except Exception:
        user_map = {}

    for i, (uid, score) in enumerate(top_users, 1):
        name = user_map.get(str(uid), f"id{uid}")
        safe_name = name.replace("[", "").replace("]", "").replace("|", "")
        rank = get_rank(score)
        lines.append(f"{i}. [id{uid}|{safe_name}] — {score} очков {rank}")

    await message.answer("🏆 Топ участников чата:\n" + "\n".join(lines))


@labeler.message(regex=r"(?i)^мура репа")
async def rep_command(message: Message):
    peer_id = message.peer_id
    text = message.text.strip()
    query = text[9:].strip()
    target_id = extract_user_id(query) if query else None
    user_id = target_id or message.from_id

    rep = get_user_reputation(peer_id, user_id)

    try:
        user = await message.ctx_api.users.get(int(user_id))
        name = f"{user[0].first_name} {user[0].last_name}"
    except Exception:
        name = f"id{user_id}"

    rank = get_rank(rep)
    safe_name = name.replace("[", "").replace("]", "").replace("|", "")
    await message.answer(f"👤 Репутация [id{user_id}|{safe_name}]: {rep} очков\n🏅 Ранг: {rank}")


@labeler.message(text=["мура ранги", "Мура ранги", "МУРА РАНГИ"])
async def ranks_command(message: Message):
    lines = ["📊 Доступные ранги:"]
    for threshold, rank in sorted(RANKS, reverse=True):
        lines.append(f"{rank} — от {threshold} очков")
    await message.answer("\n".join(lines))


@labeler.private_message(text=["админ мура топ", "Админ мура топ", "АДМИН МУРА ТОП"])
async def admin_global_top_command(message: Message):
    if message.from_id != ADMIN_USER_ID:
        return

    data = load_reputation()
    total_scores = {}

    for peer_id, users in data.items():
        for user_id, score in users.items():
            total_scores[user_id] = total_scores.get(user_id, 0) + score

    sorted_all = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)

    top_users = []
    for uid, score in sorted_all:
        try:
            user = await message.ctx_api.users.get(user_ids=[uid])
            if user and user[0].is_closed is not None:
                top_users.append((uid, score))
        except:
            continue
        if len(top_users) >= 5:
            break

    if not top_users:
        await message.answer("Пока нет глобальной репутации.")
        return

    user_ids = [int(uid) for uid, _ in top_users]

    try:
        users_info = await message.ctx_api.users.get(user_ids=user_ids)
        user_map = {str(user.id): f"{user.first_name} {user.last_name}" for user in users_info}
    except Exception:
        user_map = {}

    lines = ["🌐 Топ-5 пользователей по всем чатам:"]
    for i, (uid, total_score) in enumerate(top_users, 1):
        name = user_map.get(str(uid), f"id{uid}")
        safe_name = name.replace("[", "").replace("]", "").replace("|", "")

        best_score = 0
        for peer_id, users in data.items():
            if uid in users and users[uid] > best_score:
                best_score = users[uid]

        rank = get_rank(best_score)
        lines.append(f"{i}. [id{uid}|{safe_name}] — {total_score} очков | Ранг в активном чате: {rank}")

    await message.answer("\n".join(lines))
