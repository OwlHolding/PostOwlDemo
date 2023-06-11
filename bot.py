import telebot
import json
import sqlite3

with open('token') as f:
    bot = telebot.TeleBot(f.read())

with open('config.json') as f:
    config = json.load(f)

con = sqlite3.connect('database.db', check_same_thread=False)

def process_response(message: telebot.types.Message, group: str):
    if message.text == config[group]['buttonOK']:
        bot.send_message(message.chat.id, config[group]['messageOK'])
        with con:
            con.executemany(
                'UPDATE users SET status="subscribed" WHERE id=?', [(message.chat.id,)])
    elif message.text == config[group]['buttonCancel']:
        bot.send_message(message.chat.id, config[group]['messageCancel'])
        with con:
            con.executemany(
                'UPDATE users SET status="refused" WHERE id=?', [(message.chat.id,)])
    else:
        bot.send_message(message.chat.id, config[group]['messageUnknown'])
        bot.register_next_step_handler(message, process_response, group=group)   

@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    group = message.text.split(' ')
    if len(group) > 1:
        group = group[1]
    else:
        group = 'default'
    try:
        keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(config[group]['buttonOK'], config[group]['buttonCancel'])
        bot.send_message(
            message.chat.id, config[group]['messageHello'], reply_markup=keyboard)
        with con:
            con.executemany(
                'INSERT OR REPLACE INTO users (id, username, status) values(?, ?, ?)', 
                [(message.chat.id, message.chat.username, "launched")])
        bot.register_next_step_handler(message, process_response, group=group)
    except KeyError:
        pass

bot.infinity_polling()