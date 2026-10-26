import time
import requests
import feedparser
import telebot
from telebot import types

# ----------------- НАЛАШТУВАННЯ -----------------
TOKEN =8823364219:AAEeaC5VOgpNA4GBv8hNvgxSClcTmnhKCkg
RSS_NEWS_URL = "https://suspilne.media/rss"
# ------------------------------------------------

bot = telebot.TeleBot(TOKEN)

# Словник для збереження стану тривог по всій країні {"Область": True/False}
global_alerts_state = {}
last_news_link = None

# Словник вибору користувачів: {chat_id: "Назва області" або "Вся Україна"}
user_subscriptions = {}

# Список областей для кнопок
REGIONS_LIST = [
    "м. Київ", "Київська область", "Львівська область", "Одеська область",
    "Харківська область", "Дніпропетровська область", "Запорізька область",
    "Вінницька область", "Волинська область", "Житомирська область",
    "Закарпатська область", "Івано-Франківська область", "Кіровоградська область",
    "Луганська область", "Миколаївська область", "Полтавська область",
    "Рівненська область", "Сумська область", "Тернопільська область",
    "Херсонська область", "Хмельницька область", "Черкаська область",
    "Чернівецька область", "Чернігівська область", "Автономна Республіка Крим"
]

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    if chat_id not in user_subscriptions:
        user_subscriptions[chat_id] = "Вся Україна"
    
    send_region_menu(chat_id, "👋 Привіт! Я моніторю тривоги та новини.\n\nОберіть область, по якій хочете отримувати сповіщення:")

def send_region_menu(chat_id, text):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Кнопка «Вся Україна»
    markup.add(types.InlineKeyboardButton("🌍 Вся Україна", callback_data="sub_Вся Україна"))
    
    # Додаємо кнопки областей
    buttons = []
    for reg in REGIONS_LIST:
        buttons.append(types.InlineKeyboardButton(reg, callback_data=f"sub_{reg}"))
    markup.add(*buttons)
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("sub_"))
def callback_set_region(call):
    chat_id = call.message.chat.id
    selected_region = call.data.replace("sub_", "")
    
    user_subscriptions[chat_id] = selected_region
    
    bot.answer_callback_query(call.id, f"Збережено: {selected_region}")
    bot.send_message(
        chat_id, 
        f"✅ Готово! Тепер ви отримуватимете сповіщення для: <b>{selected_region}</b>.\n\n(Якщо захочете змінити — просто напишіть /start)",
        parse_mode="HTML"
    )

def check_all_alerts():
    global global_alerts_state
    try:
        response = requests.get("https://ubilling.net.ua/aerialalerts/", timeout=10)
        data = response.json()
        states = data.get("states", {})

        for region_name, region_info in states.items():
            is_active = region_info.get("alert", False)

            if region_name not in global_alerts_state:
                global_alerts_state[region_name] = is_active
                continue

            if global_alerts_state[region_name] != is_active:
                global_alerts_state[region_name] = is_active
                
                for chat_id, sub_region in user_subscriptions.items():
                    if sub_region == "Вся Україна" or sub_region == region_name:
                        if is_active:
                            bot.send_message(chat_id, f"🚨 <b>УВАГА! Повітряна тривога:</b>\n📍 {region_name}", parse_mode="HTML")
                        else:
                            bot.send_message(chat_id, f"✅ <b>ВІДБІЙ повітряної тривоги:</b>\n📍 {region_name}", parse_mode="HTML")

    except Exception as e:
        print(f"Помилка перевірки тривог: {e}")

def check_news():
    global last_news_link
    try:
        feed = feedparser.parse(RSS_NEWS_URL)
        if feed.entries:
            latest = feed.entries[0]
            link = latest.link
            title = latest.title

            if last_news_link is None:
                last_news_link = link
            elif last_news_link != link:
                last_news_link = link
                msg = f"📰 <b>Останні новини:</b>\n\n{title}\n\n🔗 <a href='{link}'>Читати далі</a>"
                for chat_id in user_subscriptions.keys():
                    try:
                        bot.send_message(chat_id, msg, parse_mode="HTML")
                    except Exception:
                        pass
    except Exception as e:
        print(f"Помилка перевірки новин: {e}")

if __name__ == "__main__":
    print("Бот запущений з вибором областей...")
    
    last_check_time = 0
    
    while True:
        try:
            if time.time() - last_check_time > 30:
                check_all_alerts()
                check_news()
                last_check_time = time.time()
                
            bot.poll(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"Помилка циклу: {e}")
            time.sleep(5)
