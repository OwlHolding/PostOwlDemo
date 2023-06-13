import telebot
import json
import sqlite3
import ssl

with open('token') as f:
    bot = telebot.TeleBot(f.read())

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


with open('ssl-config.json', 'rb') as file:
    ssl_config = json.load(file)


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(ssl_config['ssl-cert'], ssl_config['ssl-private'])

bot.run_webhooks(
    listen='0.0.0.0',
    port=80,
    certificate_key=ssl_config['ssl-private'],
    certificate=ssl_config['ssl-cert'],
    webhook_url='https://owl-space.ru/'
)