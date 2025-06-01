import os
import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler
)
from telegram import Update
from fastapi import FastAPI, Request
import uvicorn
import asyncio

from bot_logic import (  # обязательно правильное имя файла
    start, choose_language, select_type, select_diameter,
    select_sn, ask_length, cancel,
    CHOOSE_LANG, SELECT_TYPE, SELECT_DIAMETER, SELECT_SN, ASK_LENGTH
)

TOKEN = os.getenv("BOT_TOKEN") or "8135113589:AAGco0L8W1JTGnhOhGD_oMp6cRrhfc21_2s"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = "https://tojplast-bot.onrender.com/webhook"

application = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSE_LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
        SELECT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_type)],
        SELECT_DIAMETER: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_diameter)],
        SELECT_SN: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_sn)],
        ASK_LENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_length)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)
application.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url=WEBHOOK_URL
)


fastapi_app = FastAPI()

@fastapi_app.on_event("startup")
async def on_startup():
    await application.bot.delete_webhook()  # Удалить старый вебхук
    await application.bot.set_webhook(WEBHOOK_URL)  # Установить новый
    print(f"🚀 Webhook set to {WEBHOOK_URL}")

@fastapi_app.post(WEBHOOK_PATH)
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# Запуск локально
if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL
    )
