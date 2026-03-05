import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load .env locally if it exists
load_dotenv()

# Get variables from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY")

if not BOT_TOKEN or not TRANSLATE_API_KEY:
    raise ValueError("BOT_TOKEN or TRANSLATE_API_KEY missing")

# Setup Logging
logging.basicConfig(level=logging.WARNING)

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
        "target_language": "fr"
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(url, json=payload, headers=headers, timeout=20.0)

        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("translated_text")
        else:
            translated_text = None

    except Exception:
        translated_text = None

    if not translated_text:
        translated_text = "Sorry, I couldn't translate your text at the moment."

    await update.message.reply_text(translated_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me English text for Tigrinya translation.")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))


if __name__ == "__main__":
    print("--- Bot is now LIVE ---")
    app.run_polling(drop_pending_updates=True)