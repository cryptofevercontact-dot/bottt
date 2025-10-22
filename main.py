import os
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request, send_file
from io import BytesIO

# Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 5000))

# Inicializar Flask y Telegram
app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot de Telegram.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos disponibles:\n/start\n/help\n/datos\n/grafico")

async def datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ejemplo de DataFrame
    df = pd.DataFrame({
        "Nombre": ["Alice", "Bob", "Charlie"],
        "Edad": [25, 30, 35]
    })
    await update.message.reply_text(f"Datos:\n{df.to_string(index=False)}")

async def grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = pd.DataFrame({
        "Nombre": ["Alice", "Bob", "Charlie"],
        "Edad": [25, 30, 35]
    })

    plt.figure(figsize=(6,4))
    plt.bar(df["Nombre"], df["Edad"])
    plt.title("Edad por Nombre")
    plt.ylabel("Edad")

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    await update.message.reply_photo(photo=buffer)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

# Agregar handlers
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("help", help_command))
app_telegram.add_handler(CommandHandler("datos", datos))
app_telegram.add_handler(CommandHandler("grafico", grafico))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Ruta para webhook
@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_telegram.bot)
    app_telegram.update_queue.put(update)
    return "ok"

# Iniciar Flask y configurar webhook
if __name__ == "__main__":
    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    app_telegram.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook configurado en: {WEBHOOK_URL}")
    app_flask.run(host="0.0.0.0", port=PORT)
