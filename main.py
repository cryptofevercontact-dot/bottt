import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- Configuración ---
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"
WEBHOOK_URL = "https://suignal.onrender.com/8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"

# --- Inicializamos Flask ---
app = Flask(__name__)

# --- Inicializamos el bot ---
bot_app = ApplicationBuilder().token(TOKEN).build()

# --- Handlers del bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Bot desplegado correctamente 🚀")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Has escrito: {update.message.text}")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Ruta del webhook ---
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.update_queue.put(update)
    return "OK"

# --- Main para iniciar webhook ---
if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    async def main():
        # Configurar webhook correctamente (esperar el await)
        await bot_app.bot.set_webhook(WEBHOOK_URL)
        print(f"Webhook configurado en: {WEBHOOK_URL}")

        # Ejecutar Flask en el puerto de Render
        port = int(os.environ.get("PORT", 5000))
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        await serve(app, config)

    asyncio.run(main())
