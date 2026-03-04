import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import dotenv_values

# -----------------------------
# Load environment variables
# -----------------------------
config = dotenv_values(".env")  # reads .env as a dict
BOT_TOKEN = config.get("BOT_TOKEN")
TRANSLATE_API_KEY = config.get("TRANSLATE_API_KEY")  # your TranslateAPI.ai key

if not BOT_TOKEN or not TRANSLATE_API_KEY:
    raise ValueError("BOT_TOKEN or TRANSLATE_API_KEY not found in .env file")

# -----------------------------
# Telegram bot handlers
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a message and I will translate it to Tigrinya."
    )

# --- HELP COMMAND ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use this bot:\n"
        "1. Send any English text → I will translate it to Tigrinya.\n"
        "2. Use /start to see the welcome message.\n"
        "3. Use /about to learn more about this bot."
    )

# --- ABOUT COMMAND ---
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This is a friendly Tigrinya translator bot 😎\n"
        "Send me English text and I will translate it to Tigrinya.\n"
        "Built with ❤️ using Telegram and TranslateAPI.ai"
    )

# --- AUTO-TRANSLATE HANDLER ---
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    url = "https://api.translateapi.ai/api/v1/translate/"
    headers = {
        "Authorization": f"Bearer {TRANSLATE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "source_language": "en",
        "target_language": "ti"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 401:
            await update.message.reply_text("API key is invalid or unauthorized.")
            return

        if response.status_code != 200:
            await update.message.reply_text(f"Error: {response.status_code}\n{response.text}")
            return

        data = response.json()
        translated_text = data.get("translated_text")

        if not translated_text:
            translated_text = str(data)  # show raw response for debugging

    except Exception as e:
        translated_text = f"Translation failed: {e}"

    await update.message.reply_text(translated_text)

# -----------------------------
# Setup bot
# -----------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Clear pending updates to avoid conflicts
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about))

# Auto-translate normal messages
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

# -----------------------------
# Run bot
# -----------------------------
if __name__ == "__main__":
    app.run_polling(drop_pending_updates=True)