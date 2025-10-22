from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import os

TOKEN = os.getenv("8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y")

# Configuración de logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Bot iniciado 🚀")

def main():
    # Creamos la aplicación
    app = Application.builder().token(TOKEN).build()

    # Añadimos handlers
    app.add_handler(CommandHandler("start", start))

    # Ejecutamos el bot
    app.run_polling()

if __name__ == "__main__":
    main()
