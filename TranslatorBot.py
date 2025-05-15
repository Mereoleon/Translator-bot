from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from deep_translator import GoogleTranslator
import random

BOT_TOKEN = ' __________________________ '  

# хранилище языков 
user_languages = {}

# поддерживаемые языки
language_options = {
    "en": "🇬🇧 English",
    "de": "🇩🇪 German",
    "fr": "🇫🇷 French",
    "es": "🇪🇸 Spanish",
    "zh": "🇨🇳 Chinese",
    "ar": "🇸🇦 Arabic",
    "ja": "🇯🇵 Japanese",
    "ru": "🇷🇺 Russian",
    "cat": "🐱 Cat Language"  
}

# Главное меню с кнопками
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Начать"), KeyboardButton("Выбрать язык")],
        [KeyboardButton("Помощь")]
    ],
    resize_keyboard=False
)

# /start 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот-переводчик.\n\n"
        "Отправь мне текст — я переведу его на выбранный язык.\n\n"
        "Используй кнопки или команды:\n"
        "/setlang — выбрать язык\n"
        "/help — помощь",
        reply_markup=main_keyboard
    )

# /help 
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Помощь по боту</b>\n\n"
        "Я перевожу текст на выбранный язык\n\n"
        "<b>Команды:</b>\n"
        "• Начать — инструкция\n"
        "• Выбрать язык — кнопки выбора\n"
        "• Помощь — это сообщение\n\n"
        "Просто отправь текст — я переведу его!",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )

# /setlang
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=code)]
        for code, name in language_options.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери язык перевода:", reply_markup=reply_markup)

# обработка кнопки языка
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data
    user_id = query.from_user.id
    user_languages[user_id] = lang_code
    await query.edit_message_text(f"Язык перевода установлен: {language_options[lang_code]}")

# перевод на кошачий
def translate_to_cat_language(text: str) -> str:
    sounds = ["мяу", "мрр", "пурр", "шшш", "фрр", "мяяяу"]
    words = text.split()
    cat_translation = [random.choice(sounds) for _ in words]
    return ' '.join(cat_translation)

# обработка текстов
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # обработка кнопок меню
    if text == "Начать":
        await start(update, context)
        return
    elif text == "Помощь":
        await help_handler(update, context)
        return
    elif text == "Выбрать язык":
        await set_language(update, context)
        return

    # получаем язык
    target_lang = user_languages.get(user_id, "ru")

    try:
        if target_lang == "cat":
            translated = translate_to_cat_language(text)
        else:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)

        lang_name = language_options.get(target_lang, target_lang)
        await update.message.reply_text(f"Перевод ({lang_name}):\n{translated}")
    except Exception as e:
        await update.message.reply_text("Ошибка перевода. Попробуй позже.")
        print("Ошибка:", e)

# настройка приложения
app = ApplicationBuilder().token(BOT_TOKEN).build()

# хендлеры
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_handler))
app.add_handler(CommandHandler("setlang", set_language))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

print("Бот запущен")
app.run_polling()