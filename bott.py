import os
import httpx  # Switched to async-friendly library
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import dotenv_values

config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")
TRANSLATE_API_KEY = config.get("TRANSLATE_API_KEY")

if not BOT_TOKEN or not TRANSLATE_API_KEY:
    raise ValueError("BOT_TOKEN or TRANSLATE_API_KEY not found in .env file")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me English text and I'll translate it to Tigrinya. Use /help for more info.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use:\n1. Send English text.\n2. Get Tigrinya back.\nCommands: /start, /about, /help"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tigrinya Translator Bot 😎\nBuilt with Python & TranslateAPI.ai")

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    url = "https://api.translateapi.ai/api/v1/translate/"
    headers = {"Authorization": f"Bearer {TRANSLATE_API_KEY}"}
    payload = {"text": text, "source_language": "en", "target_language": "ti"}

    try:
        # Using async client so the bot doesn't freeze for other users
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=15.0)
            
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("translated_text", "Could not find translation in response.")
        else:
            translated_text = f"Error {response.status_code}: {response.text}"

    except Exception as e:
        translated_text = f"Connection failed: {e}"

    await update.message.reply_text(translated_text)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# REGISTER ALL HANDLERS
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command)) # Added
app.add_handler(CommandHandler("about", about))       # Added
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

if __name__ == "__main__":
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)
