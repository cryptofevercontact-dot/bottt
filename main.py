import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === CONFIGURACIÓN ===
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"  # 👈 reemplaza por tu token real

# Configuración básica de logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! 👋 El bot está funcionando correctamente.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aquí iría la ayuda del bot.")

# === MAIN ===
async def main():
    app = Application.builder().token(TOKEN).build()

    # Comandos básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Arranca el bot
    logger.info("Bot iniciado 🚀")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
