from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Token inventado, reemplaza por tu token real cuando puedas
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot de prueba 🚀")

async def main():
    # Construimos la aplicación sin usar Updater directamente
    app = Application.builder().token(TOKEN).build()

    # Añadimos un comando simple
    app.add_handler(CommandHandler("start", start))

    # Ejecutamos el bot en modo polling
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
