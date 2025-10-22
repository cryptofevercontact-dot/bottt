import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot desde variables de entorno
TOKEN = os.environ.get("8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("¡Hola! Soy tu bot funcionando en Python 3.11 🚀")

# Función principal
async def main() -> None:
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()

    # Agregar manejador de comandos
    app.add_handler(CommandHandler("start", start))

    # Ejecutar bot
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
