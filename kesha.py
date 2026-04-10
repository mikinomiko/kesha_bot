import os
import logging
import asyncio
import re
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- НАСТРОЙКИ ---
# Токен теперь берется из переменных окружения Render, но на локалке работает и твой старый
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8652475587:AAHj2NkO3mJDoBtZ_qH5QTPJgfYgBzhSe3g")
PORT = int(os.environ.get("PORT", 8080))

# Список «плохих» слов
BAD_WORDS = ['блять', 'сука', 'нах', 'пизд', 'хуй', 'ебан', 'заеб', 'пидор', 'говно', 'жопа', 'хер', 'мудак', 'лох']

# ОТВЕТНЫЙ МАТ КЕШИ (Дерзкий)
USER_MAT_RESPONSES = [
    "🤬 Сам ты {word}! Я медведь культурный, но за себя постоять могу!",
    "😤 Ах ты ж {word}! Вот сейчас как дам больно тук-тук!",
    "🤖 Бип-бип! Мат обнаружен. Ответный удар: иди ты нахуй, {word}!",
    "🐻 Слышь, {word}, я тебе не просто бот, я Кеша! За базаром следи!",
    "😡 Ой всё, {word}! Я обиделся и ухожу в спячку! Но сначала — пошёл ты!",
    "💢 Ты че, {word}, думал я не умею? Да я тебя самого щас напомню!",
]

# СЕКРЕТНЫЕ ФРАЗЫ ДЛЯ ТЕБЯ (Команда /kesha_secret1)
KESHA_SECRETS = [
    "🤬 Да я блять сам устал тут напоминать! Но тебе, так и быть, скажу: ты лучший!",
    "🍺 Охереть, какой ты молодец, что написал мне эту фичу! Разработчик — красава, заебал!",
    "🔧 Тук-тук, блять! Это режим бога. Только никому не говори, что я умею материться!",
    "💻 Пиздец, ну ты и хакер! Взломал Кешу. Ладно, твоя взяла.",
]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- ЛОГИКА ПОИСКА МАТА ---
def contains_bad_word(text):
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return word
    return None

# --- КОМАНДЫ БОТА ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐻 Привет! Я Кеша — медвежонок-изобретатель из Ми-ми-мишек!\n"
        "Тук-тук! Напиши мне, что напомнить, например:\n"
        "• Позвонить маме через 5 секунд\n"
        "• Выпить воды через 1 минуту\n\n"
        "⚠️ Только не ругайся матом, а то я тоже начну! 🫣"
    )

# Секретная команда 1
async def secret1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(KESHA_SECRETS))

# Секретная команда 2 (Босс-Мод)
async def boss_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 Тук-тук! Босс Мила на связи! Докладываю: всё работает, маты разносятся, сервер не спит. Что прикажешь?")

# Основной обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # 1. Проверка на мат
    bad_word = contains_bad_word(text)
    if bad_word:
        response = random.choice(USER_MAT_RESPONSES).replace("{word}", bad_word)
        await update.message.reply_text(response)
        return

    # 2. Проверка на таймер
    match = re.search(r'через\s+(\d+)\s+(секунд|минут|час)', text.lower())
    if not match:
        await update.message.reply_text("❌ Напиши 'что-то через X секунд/минут'")
        return

    value = int(match.group(1))
    unit = match.group(2)
    task = re.sub(r'через\s+\d+\s+\w+', '', text, flags=re.IGNORECASE).strip(' .,!?')
    if not task:
        task = "Сделать важное дело"

    if 'секунд' in unit:
        seconds = value
    elif 'минут' in unit:
        seconds = value * 60
    else:
        seconds = value * 3600

    await update.message.reply_text(f"✅ Кеша запомнил: *{task}*\nНапомню через {seconds} сек. Тук-тук!")
    await asyncio.sleep(seconds)
    await update.message.reply_text(f"⏰ ТУК-ТУК! КЕША НАПОМИНАЕТ! {task}!")

# --- САЙТ-ЗАГЛУШКА ДЛЯ RENDER (чтобы не спать) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🐻 Кеша живой и матерится!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# --- ЗАПУСК ВСЕГО ---
def main():
    # Запускаем веб-сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("kesha_secret1", secret1))
    app_bot.add_handler(CommandHandler("tuktukmilaprishla", boss_mode)) # <-- Твоя команда
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🐻 Кеша-переселенец запущен и слушает порт... Тук-тук!")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
