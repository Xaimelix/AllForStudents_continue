import telebot
from telebot import types
from dotenv import load_dotenv
import os
from data.help_requests import HelpRequests
from data import db_session
import datetime
import time

load_dotenv('config.env')
API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

user_texts = {}  # user_id -> текст

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "db/database.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Привет! Это бот для отправки сообщения в поддержку. Просто напиши свой вопрос или проблему, и я помогу отправить его в поддержку!")

@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, "Просто напиши свой вопрос или проблему. Я предложу отправить его в поддержку.")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.text.startswith('/'):
        bot.send_message(message.chat.id, "Команда не распознана. Попробуйте /help.")
        return

    user_texts[message.chat.id] = (message.text, f'{message.from_user.username} ({message.from_user.first_name} {message.from_user.last_name})' if message.from_user.username else None)

    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Да", callback_data='send_help')
    no_button = types.InlineKeyboardButton("Нет", callback_data='cancel_help')
    markup.add(yes_button, no_button)

    bot.send_message(message.chat.id, f"Вы написали: \n\n{message.text}\n\nОтправить это в поддержку?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    chat_id = call.message.chat.id

    if call.data == 'send_help':
        text = user_texts.get(chat_id)[0]
        name = user_texts.get(chat_id)[1] if user_texts.get(chat_id) else None
        if text:
            db_sess = db_session.create_session()
            help_request = HelpRequests(user_id=chat_id, text=text, created_at=datetime.datetime.now(), name=name)
            db_sess.add(help_request)
            db_sess.commit()
            bot.edit_message_text("Ваше сообщение отправлено в поддержку.", chat_id, call.message.message_id)
            user_texts.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "Не найдено сообщение для отправки.")

    elif call.data == 'cancel_help':
        bot.edit_message_text("Отправка отменена.", chat_id, call.message.message_id)
        user_texts.pop(chat_id, None)


def reply_check_loop():
    while True:
        try:
            init_db()
            db_sess = db_session.create_session()
            replies = db_sess.query(HelpRequests).filter(
                HelpRequests.status == "closed",
                HelpRequests.reply != None,
                HelpRequests.is_replied == False
            ).all()

            for r in replies:
                try:
                    bot.send_message(r.user_id, f"Ответ поддержки:\n\n{r.reply}")
                    r.is_replied = True
                    db_sess.commit()
                    db_sess.close()
                except Exception as e:
                    print(f"Ошибка при отправке ответа: {e}")
        except Exception as e:
            print(f"Ошибка в reply_check_loop: {e}")

        time.sleep(10)  # Проверять каждые 10 секунд

def run_bot():
    try:
        init_db()
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")
