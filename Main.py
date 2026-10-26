import time
import requests
import feedparser
import telebot
from telebot import types

# ----------------- НАЛАШТУВАННЯ -----------------
TOKEN = "8823364219:AAEeaC5VOgpNA4GBv8hNvgxSClcTmnhKCkg"
RSS_NEWS_URL = "https://suspilne.media/rss"
# ------------------------------------------------

bot = telebot.TeleBot(TOKEN)

# Словник для збереження стану тривог по всій країні
global_alerts_state = {}
last_news_link = None


@bot.message_handler(commands=['start'])
def send_welcome(markup):
    bot.reply_to(markup, "Привіт! Я бот для моніторингу повітряних тривог та новин. Працюю 24/7 у хмарі!")


# Запуск бота в нескінченному циклі опитування
if __name__ == "__main__":
    print("Бот запущено та готовий до роботи!")
    bot.infinity_polling()
