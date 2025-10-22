import asyncio
import numpy as np
import pandas as pd
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "TU_TOKEN_AQUI"  # <--- Pon aquí tu token de Telegram

def prediccion_sui_simple():
    try:
        data = yf.download("SUI-USD", period="max", interval="1h", auto_adjust=True)
        price_col = None
        for col in ["Close", "Adj Close", "Price", "Last"]:
            if col in data.columns:
                price_col = col
                break
        if price_col is None:
            numeric_cols = data.select_dtypes(include=np.number).columns
            if len(numeric_cols) == 0:
                return "No hay datos de precio disponibles."
            price_col = numeric_cols[0]

        data = data[data[price_col] > 0].dropna(subset=[price_col])
        if data.empty:
            return "No se descargaron datos válidos."

        prices = data[price_col].values
        logr = np.diff(np.log(prices))
        states = pd.qcut(logr, q=5, labels=False, duplicates="drop") + 1
        num_states = len(np.unique(states))

        P = np.zeros((num_states, num_states))
        for i in range(len(states)-1):
            P[states[i]-1, states[i+1]-1] += 1
        P = P / P.sum(axis=1, keepdims=True)

        mu_j = [logr[states==k].mean() for k in range(1, num_states+1)]
        current_state = states[-1]
        expect_r = np.dot(P[current_state-1], mu_j)

        action = "HOLD"
        if expect_r > 0.001:
            action = "BUY"
        elif expect_r < -0.001:
            action = "SELL"

        return f"Último precio: ${prices[-1]:.4f}\nAcción sugerida: {action}"
    except Exception as e:
        return f"Error descargando datos: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot de predicción de SUI/USD.\nUsa /sui para obtener la predicción.")

async def sui(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Calculando predicción...")
    resultado = prediccion_sui_simple()
    await update.message.reply_text(resultado)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sui", sui))
    print("🚀 Bot iniciado. Esperando comandos...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
