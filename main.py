import os
import asyncio

# 👇 Fuerza la instalación de la versión correcta de la librería (soluciona el bug de Render)
os.system("pip install python-telegram-bot==20.7 --force-reinstall")

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ⚠️ Sustituye esto por tu token real del BotFather
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! 🤖 El bot está funcionando correctamente en Render 🚀")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Dijiste: {update.message.text}")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("✅ Bot iniciado y escuchando mensajes...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
