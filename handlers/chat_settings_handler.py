from vkbottle.bot import Message, BotLabeler
from utils.chat_settings import set_chat_setting, get_chat_setting
from vkbottle import VKAPIError

labeler = BotLabeler()
labeler.vbml_ignore_case = True

@labeler.message(text=["мура шанс <chance:int>", "мура шанс"])
async def set_mura_chance(message: Message, chance: int = None):
    if not message.chat_id:
        await message.answer("Эта команда работает только в беседах.")
        return

    try:
        chat_info = await message.ctx_api.messages.get_conversation_members(peer_id=message.peer_id)
        creator_id = next((m.member_id for m in chat_info.items if m.is_owner), None)
    except VKAPIError as e:
        if "access denied" in str(e).lower():
            await message.answer("Мне нужны права администратора, чтобы получить данные о беседе. Пожалуйста, дайте мне права администратора.")
            return
        await message.answer("Не удалось получить данные о беседе.")
        return

    if message.from_id != creator_id:
        await message.answer("Только создатель беседы может менять шанс.")
        return

    if chance is None:
        await message.answer("Укажи шанс от 1 до 100.")
        return

    if not (1 <= chance <= 100):
        await message.answer("Число должно быть от 1 до 100.")
        return

    set_chat_setting(str(message.peer_id), "mura_chance", chance)
    await message.answer(f"Шанс успешно установлен на {chance}%.")