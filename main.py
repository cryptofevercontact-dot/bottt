import asyncio
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# TOKEN DEL BOT (puedes reemplazarlo por el tuyo)
TOKEN = "8408629487:AAG3ljf-zZzzFZ56BESet-GSYYqD9wDGj7Y"  # Token inventado

# --- Funciones del bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de seguimiento de SUI.\n\n"
        "Usa /precio para ver el valor actual del token SUI/USD en tiempo real."
    )

async def precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ticker = yf.Ticker("SUI-USD")
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            await update.message.reply_text("❌ No se pudo obtener el precio ahora mismo.")
            return

        precio_actual = round(data["Close"].iloc[-1], 4)
        await update.message.reply_text(f"💰 El precio actual de SUI es: **${precio_actual} USD**", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error al obtener el precio: {e}")

# --- Función principal ---
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("precio", precio))

    print("✅ Bot iniciado y ejecutándose...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
