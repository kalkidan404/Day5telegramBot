import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import dotenv_values

# 1. Load environment variables
config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")
TRANSLATE_API_KEY = config.get("TRANSLATE_API_KEY")

if not BOT_TOKEN or not TRANSLATE_API_KEY:
    raise ValueError("BOT_TOKEN or TRANSLATE_API_KEY not found in .env file")

# 2. Setup Logging
logging.basicConfig(level=logging.WARNING)

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # URL MUST HAVE THE TRAILING SLASH FOR THIS API
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
            try:
                data = response.json()
                translated_text = data.get("translated_text") 
            except Exception:
                translated_text = None
        else:
            translated_text = None

    except Exception as e:
        translated_text = None
        if not translated_text:
            translated_text="Sorry, I couldn't translate your text at the moment. Please try again later."

    await update.message.reply_text(translated_text)

# -----------------------------
# Bot Setup
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me English text for Tigrinya translation.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

if __name__ == "__main__":
    print("--- Bot is now LIVE on your PC ---")
    app.run_polling(drop_pending_updates=True)
