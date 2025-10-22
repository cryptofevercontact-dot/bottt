#!/usr/bin/env python3
"""
bot_sui_telegram_async.py
Bot de Telegram SUI (Markov + Monte Carlo 7d) adaptado a python-telegram-bot v20+ y async.
"""

import os
import io
import logging
from datetime import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sui_bot_async")

# ---------------------------
# Helpers: CoinGecko fetch + pipeline
# ---------------------------
def fetch_sui_hourly(hours_back=4000):
    coin_id = "sui"
    vs_currency = "usd"
    # Precio actual
    url_price = "https://api.coingecko.com/api/v3/simple/price"
    params_p = {"ids": coin_id, "vs_currencies": vs_currency}
    r1 = requests.get(url_price, params=params_p, timeout=10)
    r1.raise_for_status()
    last_price = float(r1.json()[coin_id][vs_currency])
    # Historial
    now_ts = int(datetime.utcnow().timestamp())
    since_ts = now_ts - hours_back * 3600
    url_hist = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params_h = {"vs_currency": vs_currency, "from": since_ts, "to": now_ts}
    r2 = requests.get(url_hist, params=params_h, timeout=30)
    r2.raise_for_status()
    hist = r2.json().get("prices", [])
    if not hist:
        raise RuntimeError("CoinGecko no devolvió histórico.")
    df = pd.DataFrame(hist, columns=["ts_ms", "price"])
    df["dt"] = pd.to_datetime(df["ts_ms"], unit="ms", utc=True)
    df.set_index("dt", inplace=True)
    hourly = df["price"].resample("1H").last().ffill().bfill()
    hourly = hourly[-hours_back:]
    return last_price, hourly

def run_markov_montecarlo(prices_series, K=5, n_sim=1000, n_days=7):
    prices = prices_series.values.astype(float)
    prices = np.where(prices <= 0, np.nan, prices)
    prices = pd.Series(prices).ffill().bfill().values
    logr = np.diff(np.log(prices + 1e-12))
    if len(logr) < 30:
        raise RuntimeError("Datos insuficientes para modelar (menos de 30 retornos).")
    try:
        states = pd.qcut(logr, q=K, labels=False, duplicates="drop") + 1
    except Exception:
        states = pd.Series(logr).rank().astype(int).values
    states = np.array(states)
    num_states = len(np.unique(states))
    P = np.zeros((num_states, num_states))
    for i in range(len(states)-1):
        P[states[i]-1, states[i+1]-1] += 1
    row_sums = P.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = P / row_sums
    mu_j = np.array([np.mean(logr[states==k]) if np.any(states==k) else 0.0 for k in range(1, num_states+1)])
    sigma = np.std(logr)
    current_state = int(states[-1])
    p_up = float(P[current_state-1, mu_j>0].sum())
    p_down = float(P[current_state-1, mu_j<0].sum())
    expect_r = float(np.dot(P[current_state-1], mu_j))
    conf = float(P[current_state-1].max())
    entropy = float(-(P[current_state-1]*np.log2(P[current_state-1]+1e-12)).sum())
    mc_returns = np.zeros((n_sim, n_days))
    rng = np.random.default_rng(42)
    for s in range(n_sim):
        st = current_state - 1
        for d in range(n_days):
            st = rng.choice(np.arange(num_states), p=P[st])
            mc_returns[s, d] = mu_j[st] + rng.normal(0, sigma)
    mc_acc = np.cumprod(1 + mc_returns, axis=1) - 1
    percentiles = np.percentile(mc_acc, [5,50,95], axis=0)
    recent_count = None
    if len(states) >= 24:
        recent_states = pd.Series(states[-24:])
        recent_count = recent_states.value_counts().sort_index().to_dict()
    return {
        "num_states": num_states,
        "P": P,
        "mu_j": mu_j,
        "current_state": current_state,
        "p_up": p_up,
        "p_down": p_down,
        "expect_r": expect_r,
        "conf": conf,
        "entropy": entropy,
        "percentiles": percentiles,
        "mc_acc": mc_acc,
        "recent_count": recent_count
    }

def plot_mc(percentiles, last_price, title="Monte Carlo 7 días (retorno acumulado %)"):
    days = np.arange(1, percentiles.shape[1]+1)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(days, percentiles[1]*100, label="Mediana (50%)", color="tab:blue", linewidth=2)
    ax.fill_between(days, percentiles[0]*100, percentiles[2]*100, color="tab:blue", alpha=0.2, label="5%-95%")
    ax.axhline(0, color="k", linestyle="--", linewidth=0.7)
    ax.set_xlabel("Día")
    ax.set_ylabel("Retorno acumulado (%)")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend()
    bio = io.BytesIO()
    plt.tight_layout()
    fig.savefig(bio, format="png", dpi=150)
    plt.close(fig)
    bio.seek(0)
    return bio

# ---------------------------
# Handlers Async
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola — soy el bot Markov+MC para SUI.\nComando:\n/sui - análisis actual SUI (precio + MC 7d)\n/help - esta ayuda"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /sui para obtener el análisis actual de SUI.")

async def sui_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Procesando datos…")
    try:
        last_price, hourly = fetch_sui_hourly(hours_back=4000)
        res = run_markov_montecarlo(hourly, K=5, n_sim=1200, n_days=7)
        text = f"*SUI / USD — Análisis en tiempo real*\nÚltimo precio: *${last_price:.4f}*\n"
        text += f"Estado actual: *{res['current_state']}* (K={res['num_states']})\n\n"
        text += f"Prob. subida: *{res['p_up']*100:.1f}%* | Prob. bajada: *{res['p_down']*100:.1f}%*\n"
        text += f"Retorno esperado (1-step): *{res['expect_r']*100:.3f}%*\n"
        text += f"Confianza: *{res['conf']*100:.1f}%* | Entropía: *{res['entropy']:.3f}*\n\n"
        percs = res["percentiles"]
        text += "*Monte Carlo 7 días (retorno acumulado %)*\n"
        for i in range(percs.shape[1]):
            text += f"Día {i+1}: Peor {percs[0,i]*100:+.2f}% | Típico {percs[1,i]*100:+.2f}% | Mejor {percs[2,i]*100:+.2f}%\n"
        if res["recent_count"] is not None:
            text += "\nÚltimas 24h - conteo de estados: " + ", ".join([f"Est{int(k)}:{v}" for k,v in res["recent_count"].items()])
        img = plot_mc(percs, last_price)
        await update.message.reply_photo(photo=img, caption=text, parse_mode=ParseMode.MARKDOWN)
        await msg.delete()
    except Exception as e:
        logger.exception("Error en /sui")
        await msg.delete()
        await update.message.reply_text(f"Error procesando /sui: {e}")

# ---------------------------
# Main Async
# ---------------------------
async def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Define TELEGRAM_BOT_TOKEN con el token del BotFather")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("sui", sui_cmd))
    logger.info("Bot iniciado 🚀")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
