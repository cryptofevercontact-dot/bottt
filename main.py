import os
import pandas as pd
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token desde variable de entorno
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("No se encontró TELEGRAM_TOKEN en las variables de entorno.")

# Función de predicción usando CSV
def prediccion_sui_csv(csv_path="sui_usd_historico.csv"):
    data = pd.read_csv(csv_path, parse_dates=True)
    price_col = "Close"
    data = data[data[price_col] > 0].dropna(subset=[price_col])
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
    p_up = sum(P[current_state-1, np.array(mu_j)>0])
    p_down = sum(P[current_state-1, np.array(mu_j)<0])
    expect_r = np.dot(P[current_state-1], mu_j)
    conf = P[current_state-1].max()
    entropy = -(P[current_state-1]*np.log2(P[current_state-1]+1e-10)).sum()

    action = "HOLD"
    if expect_r > 0.001:
        action = "BUY"
    elif expect_r < -0.001:
        action = "SELL"

    n_days = 7
    n_sim = 1000
    sigma = np.std(logr)
    mc_returns = np.zeros((n_sim, n_days))
    for s in range(n_sim):
        st = current_state-1
        for d in range(n_days):
            st = np.random.choice(num_states, p=P[st])
            mc_returns[s,d] = mu_j[st] + np.random.normal(0, sigma)
    percentiles = np.percentile(mc_returns, [5,50,95], axis=0)

    output = f"✅ Último precio: ${prices[-1]:.2f}\n"
    output += "📈 Predicción SUI/USD - Próximos 7 días (Monte Carlo)\n"
    output += "Día | Peor caso (5%) | Escenario medio (50%) | Mejor caso (95%)\n"
    for i in range(n_days):
        output += f"{i+1:>3} | {percentiles[0,i]*100:>7.2f}% | {percentiles[1,i]*100:>7.2f}% | {percentiles[2,i]*100:>7.2f}%\n"
    output += f"\nEstado actual: {current_state}\nProbabilidad subida: {p_up*100:.1f}%, probabilidad bajada: {p_down*100:.1f}%\n"
    output += f"Retorno esperado: {expect_r*100:.3f}%\nConfianza: {conf*100:.1f}%, Entropía: {entropy:.3f}\n🎯 Acción sugerida: {action}"
    return output

# Handlers de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Soy el bot SUI/USD. Usa /prediccion para ver la predicción de 7 días.")

async def prediccion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = prediccion_sui_csv("sui_usd_historico.csv")
        await update.message.reply_text(texto)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Arrancar bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("prediccion", prediccion))

print("🚀 Bot iniciado. Esperando comandos en Telegram…")
app.run_polling()
