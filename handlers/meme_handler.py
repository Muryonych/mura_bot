import random
import aiohttp
import os
from bs4 import BeautifulSoup
from vkbottle.bot import Message, BotLabeler
from vkbottle import PhotoMessageUploader

labeler = BotLabeler()
labeler.vbml_ignore_case = True

MEME_DIR = "memes"
os.makedirs(MEME_DIR, exist_ok=True)

@labeler.message(text="мура мем")
async def send_random_meme(message: Message):
    # Используем категорию "мем" на сайте
    page_num = random.randint(1, 20)
    url = f"https://joyreactor.cc/tag/мем/{page_num}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    img_tags = soup.find_all("img")
    img_urls = [
        tag["src"]
        for tag in img_tags
        if tag.get("src") and ("joyreactor.cc/pics/post" in tag["src"] or "img.joyreactor.cc" in tag["src"])
            and not tag["src"].endswith(".gif")
    ]

    if not img_urls:
        await message.answer("Не удалось найти мем 😿")
        return

    img_url = random.choice(img_urls)
    img_ext = img_url.split('.')[-1].split('?')[0]
    file_path = os.path.join(MEME_DIR, f"meme.{img_ext}")

    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as img_resp:
            with open(file_path, "wb") as f:
                f.write(await img_resp.read())

    uploader = PhotoMessageUploader(message.ctx_api)
    photo = await uploader.upload(file_path)
    await message.answer(attachment=photo)

    try:
        os.remove(file_path)
    except Exception:
        pass
