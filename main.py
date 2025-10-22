import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Obtener token desde la variable de entorno
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ No se ha encontrado el token. Asegúrate de configurar BOT_TOKEN en Render.")

# Handlers de ejemplo
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("¡Hola! Bot funcionando correctamente 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Comandos disponibles:\n/start - Iniciar el bot\n/help - Mostrar ayuda")

def main() -> None:
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()

    # Registrar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Iniciar el bot
    logger.info("Bot iniciado 🚀")
    app.run_polling()  # Esto maneja el loop de asyncio internamente

if __name__ == "__main__":
    main()
