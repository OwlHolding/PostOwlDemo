import telebot
import json
import sqlite3
import threading

with open('token') as f:
    token = f.read()

bot = telebot.TeleBot(token)

with open('replicas.json') as f:
    replicas = json.load(f)

con = sqlite3.connect('database.db', check_same_thread=False, isolation_level=None)
lock = threading.RLock()


def process_response(message: telebot.types.Message, origin: str):
    if message.text == replicas['buttonOK'] or message.text == "Да":
        bot.send_message(message.chat.id, replicas['messageOK'], 
                        reply_markup=telebot.types.ReplyKeyboardRemove())
        with lock:
            con.executemany(
                'UPDATE users SET status="subscribed" WHERE id=?', [(message.chat.id,)])
    else:
        bot.send_message(message.chat.id, replicas['unknown'])
        bot.register_next_step_handler(message, process_response, origin=origin)


@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    startmessage = message.text.split(' ')
    origin = 'None'
    if len(startmessage) > 1:
        origin = startmessage[1]
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(replicas['buttonOK'])
    bot.send_message(message.chat.id, replicas['messageHello'], reply_markup=keyboard)
    with lock:
        con.execute(
            'INSERT OR REPLACE INTO users (id, username, origin, status) values(?, ?, ?, ?)',
            (message.chat.id, message.chat.username, origin, "started"))
    bot.register_next_step_handler(message, process_response, origin=origin)        


if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling()