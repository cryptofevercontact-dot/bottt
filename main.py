import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# TOKEN inventado para pruebas
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"  # ⚠️ Este no es real

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Bot corriendo correctamente.")

async def main():
    # Construimos la aplicación con el token
    app = Application.builder().token(TOKEN).build()

    # Añadimos un comando simple
    app.add_handler(CommandHandler("start", start))

    # Ejecutamos el bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
