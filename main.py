import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters, ConversationHandler
)
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

logging.getLogger("telegram.ext").setLevel(logging.ERROR)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSE_LANG, SELECT_TYPE, SELECT_DIAMETER, SELECT_SN, ASK_LENGTH = range(5)

translations = {
    "TJK": {
        "choose_type": "Навъи лӯларо интихоб кунед:",
        "choose_diameter": "Қутри лӯларо интихоб кунед:",
        "choose_sn": "Синфи сахтӣ (SN) интихоб кунед:",
        "enter_length": "Чанд метр лозим аст?",
        "invalid_number": "Лутфан як адад ворид кунед (метр).",
        "summary": (
            "📦 Шумо интихоб кардед:\n"
            "- Навъ: *{type}*\n"
            "- Қутр(Диаметор): *{diameter} мм*\n"
            "- SN: *{sn}*\n"
            "- Дарозӣ: *{length} м*\n\n"
            "💰 Нархи умумӣ: *{total_price} сомонӣ*"
        ),
        "start": "Салом! Забонро интихоб кунед:",
        "types": ["Гофра", "Спиралӣ"]
    },
    "RU": {
        "choose_type": "Выбери тип трубы:",
        "choose_diameter": "Выбери диаметр трубы:",
        "choose_sn": "Выбери класс жесткости SN:",
        "enter_length": "Сколько метров тебе нужно?",
        "invalid_number": "Пожалуйста, введи число (в метрах).",
        "summary": (
            "📦 Вы выбрали:\n"
            "- Тип трубы: *{type}*\n"
            "- Диаметр: *{diameter} мм*\n"
            "- Жесткость: *{sn}*\n"
            "- Длина: *{length} м*\n\n"
            "💰 Стоимость: *{total_price} сомони*"
        ),
        "start": "Привет! 👋\nВыберите язык:",
        "types": ["Гофра", "Спиральная"]
    },
    "EN": {
        "choose_type": "Choose pipe type:",
        "choose_diameter": "Choose pipe diameter:",
        "choose_sn": "Choose stiffness class (SN):",
        "enter_length": "How many meters do you need?",
        "invalid_number": "Please enter a number (in meters).",
        "summary": (
            "📦 You selected:\n"
            "- Type: *{type}*\n"
            "- Diameter: *{diameter} mm*\n"
            "- Stiffness: *{sn}*\n"
            "- Length: *{length} m*\n\n"
            "💰 Total cost: *{total_price} somoni*"
        ),
        "start": "Hi! 👋\nChoose your language:",
        "types": ["Corrugated", "Spiral"]
    }
}

pipes_gofra = {
    "110": {"SN8": 45},
    "160": {"SN8": 75},
    "200": {"SN8": 120, "SN10": 120},
    "250": {"SN8": 160},
    "300": {"SN8": 230, "SN10": 230},
    "315": {"SN8": 260},
    "400": {"SN8": 380, "SN10": 380},
    "500": {"SN8": 580, "SN10": 580}
}

pipes_spiral = {
    "500": {"SN8": 580, "SN10": 580},
    "600": {"SN8": 800, "SN10": 800},
    "800": {"SN8": 1350, "SN10": 1350},
    "1000": {"SN8": 2200, "SN10": 2200},
    "1200": {"SN8": 2900, "SN10": 2900},
    "1400": {"SN8": 5000},
    "1600": {"SN8": 6000}
}

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Tajik", "Русский", "English"]]
    await update.message.reply_text(
        "👋 Please choose a language:\nВыберите язык:\nЗабонро интихоб кунед:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_LANG

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_input = update.message.text.lower()
    uid = update.effective_user.id

    lang_code = "RU"
    if "taj" in lang_input:
        lang_code = "TJK"
    elif "eng" in lang_input:
        lang_code = "EN"

    user_data[uid] = {"lang": lang_code}
    trans = translations[lang_code]

    keyboard = [[t] for t in trans["types"]]
    await update.message.reply_text(
        trans["choose_type"],
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return SELECT_TYPE

async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = user_data[uid]["lang"]
    trans = translations[lang]

    user_data[uid]["type"] = update.message.text
    data = pipes_gofra if update.message.text == trans["types"][0] else pipes_spiral
    keyboard = [[d] for d in sorted(data.keys(), key=int)]
    await update.message.reply_text(
        trans["choose_diameter"],
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return SELECT_DIAMETER

async def select_diameter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = user_data[uid]["lang"]
    trans = translations[lang]

    user_data[uid]["diameter"] = update.message.text
    pipe_type = user_data[uid]["type"]
    is_gofra = pipe_type == trans["types"][0]
    sn_options = (pipes_gofra if is_gofra else pipes_spiral)[update.message.text]
    if len(sn_options) == 1:
        user_data[uid]["sn"] = list(sn_options.keys())[0]
        await update.message.reply_text(trans["enter_length"])
        return ASK_LENGTH
    else:
        keyboard = [[sn] for sn in sn_options.keys()]
        await update.message.reply_text(
            trans["choose_sn"],
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SELECT_SN

async def select_sn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data[uid]["sn"] = update.message.text
    lang = user_data[uid]["lang"]
    await update.message.reply_text(translations[lang]["enter_length"])
    return ASK_LENGTH

async def ask_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = user_data[uid]["lang"]
    trans = translations[lang]

    try:
        length = float(update.message.text.replace(",", "."))
        user_data[uid]["length"] = length
        pipe_type = user_data[uid]["type"]
        diameter = user_data[uid]["diameter"]
        sn = user_data[uid]["sn"]
        is_gofra = pipe_type == trans["types"][0]
        price = (pipes_gofra if is_gofra else pipes_spiral)[diameter][sn]
        total_price = round(price * length, 2)

        msg = trans["summary"].format(
            type=pipe_type, diameter=diameter, sn=sn, length=length, total_price=total_price
        )
        await update.message.reply_markdown(msg)
    except ValueError:
        await update.message.reply_text(trans["invalid_number"])
        return ASK_LENGTH

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.")
    return ConversationHandler.END

if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()

    async def main():
        app = ApplicationBuilder().token("8135113589:AAGco0L8W1JTGnhOhGD_oMp6cRrhfc21_2s").build()

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

        app.add_handler(conv_handler)
        print("✅ Бот запущен.")
        await app.run_polling()

    asyncio.run(main())
