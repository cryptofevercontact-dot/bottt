# main.py
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# ----------------------------
# Funciones del bot
# ----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu bot, listo para ayudarte.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Iniciar bot\n"
        "/help - Mostrar ayuda\n"
        "/datos - Mostrar ejemplo de datos\n"
        "/grafico - Generar gráfico de ejemplo"
    )

async def datos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://jsonplaceholder.typicode.com/todos"
    response = requests.get(url)
    if response.status_code == 200:
        data = pd.DataFrame(response.json())
        muestra = data.head()
        await update.message.reply_text(
            f"Primeros 5 registros:\n{muestra.to_string()}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text("No se pudieron obtener los datos.")

async def grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.figure()
    plt.plot(x, y)
    plt.title("Gráfico de ejemplo")
    plt.xlabel("x")
    plt.ylabel("sin(x)")
    plt.grid(True)
    
    # Guardamos el gráfico en la carpeta temporal de Render
    grafico_path = os.path.join("/tmp", "grafico.png")
    plt.savefig(grafico_path)
    plt.close()

    with open(grafico_path, "rb") as f:
        await update.message.reply_photo(f)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Me has dicho: {update.message.text}")

# ----------------------------
# Configuración del bot
# ----------------------------

def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")  # mejor usar variable de entorno en Render

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("datos", datos))
    app.add_handler(CommandHandler("grafico", grafico))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == "__main__":
    main()
