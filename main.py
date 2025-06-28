import asyncio
import threading
import logging
import nest_asyncio
import os
import json

from flask import Flask, send_from_directory, jsonify
from vkbottle.bot import Bot
from handlers import register_handlers

# === Настройка логов ===
from loguru import logger
logger.remove()  # Удаляем все предыдущие логгеры
logger.add(lambda msg: print(msg, end=""), level="INFO")  # Показываем только INFO и выше

# Можно ещё настроить уровень для логгера vkbottle, если нужно:
# import sys
# logger.add(sys.stderr, level="WARNING")  # Альтернативный способ

# === Flask-приложение ===
flask_app = Flask(__name__, static_folder="frontend/build", static_url_path="/")

@flask_app.route("/")
def index():
    return send_from_directory(flask_app.static_folder, "index.html")

@flask_app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(flask_app.static_folder, path)

@flask_app.route("/api/stats")
def get_stats():
    stats_path = os.path.join("mura", "chat_stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
        return jsonify(stats)
    return jsonify([])

def run_flask():
    flask_app.run(host="0.0.0.0", port=5000, use_reloader=False, debug=False)

bot = Bot("vk1.a.XrEuZKVsYj8SMieiM726zon51s3pR30mnQqFWVmhYwhNxJyWPj-P7aXiXOZ0l-eN-iRYS2rgyQ8CM2OAi4FDJ7LA05HUxi1Z_f2L2ZYne7pmIFP8gm-vJ6oJcvmWW2MUHkufhu2fQagA7-LSwfzvqjfnyiusByiuITyO-Wqra_1jtQXHiH3AEcre-Fk2J0o935NKexYNSSoEwSVkVQA3MA")
register_handlers(bot)

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await bot.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
