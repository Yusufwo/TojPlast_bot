from dotenv import load_dotenv
load_dotenv()


import os
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler
)
from bot_logic import (
    start, choose_language, select_type, select_diameter,
    select_sn, ask_length, cancel,
    CHOOSE_LANG, SELECT_TYPE, SELECT_DIAMETER, SELECT_SN, ASK_LENGTH
)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = 'https://tojplast-bot.onrender.com'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.environ.get('PORT', 10000))

application = Application.builder().token(TOKEN).build()

# Обработчики состояний
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

if __name__ == '__main__':
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )
