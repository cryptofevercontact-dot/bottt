import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIGURACIÓN ---
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"
WEBHOOK_URL = "https://suignal.onrender.com/" + TOKEN

# --- LOGS ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- APP FLASK ---
app = Flask(__name__)

# --- BOT APP ---
application = Application.builder().token(TOKEN).build()

# --- COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuario {update.effective_user.first_name} inició el bot.")
    await update.message.reply_text("✅ ¡Bot funcionando correctamente desde Render!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Mensaje recibido: {update.message.text}")
    await update.message.reply_text(f"Has dicho: {update.message.text}")

# --- AÑADIMOS HANDLERS ---
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- RUTA WEBHOOK ---
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.update_queue.put(update)
    return "OK", 200

# --- INICIO SERVIDOR ---
async def main():
    logger.info("Configurando webhook...")
    await application.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook configurado en: {WEBHOOK_URL}")

    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    port = int(os.environ.get("PORT", 5000))
    config.bind = [f"0.0.0.0:{port}"]

    logger.info(f"Servidor Flask corriendo en puerto {port}")
    await serve(app, config)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
