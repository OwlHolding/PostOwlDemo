import telebot
import json
import sqlite3

with open('token') as f:
    token = f.read()

bot = telebot.TeleBot(token)
bot.remove_webhook()
bot.set_webhook(url=f'https://owl-space.ru:80/{token}/')

with open('config.json') as f:
    config = json.load(f)

con = sqlite3.connect('database.db', check_same_thread=False)


def process_response(message: telebot.types.Message, section: str):
    if message.text == config[section]['buttonOK']:
        bot.send_message(message.chat.id, config[section]['messageOK'])
        with con:
            con.executemany(
                'UPDATE users SET status="subscribed" WHERE id=?', [(message.chat.id,)])
    elif message.text == config[section]['buttonCancel']:
        bot.send_message(message.chat.id, config[section]['messageCancel'])
        with con:
            con.executemany(
                'UPDATE users SET status="refused" WHERE id=?', [(message.chat.id,)])
    else:
        bot.send_message(message.chat.id, config[section]['messageUnknown'])
        bot.register_next_step_handler(message, process_response, section=section)


@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    section = message.text.split(' ')
    if len(section) > 1:
        section = section[1]
    else:
        section = 'default'
    try:
        keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(config[section]['buttonOK'], config[section]['buttonCancel'])
        bot.send_message(
            message.chat.id, config[section]['messageHello'], reply_markup=keyboard)
        with con:
            con.executemany(
                'INSERT OR REPLACE INTO users (id, username, section, status) values(?, ?, ?, ?)',
                [(message.chat.id, message.chat.username, section, "launched")])
        bot.register_next_step_handler(message, process_response, section=section)
    except KeyError:
        pass

if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling()