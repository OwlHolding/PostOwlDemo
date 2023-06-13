from fastapi import FastAPI
import json
from bot import bot
import telebot
import uvicorn

app = FastAPI()

with open('app-config.json', 'rb') as file:
    config = json.load(file)

with open('token', 'r') as file:
    token = file.read()


@app.post(f'/{token}/')
async def handler(update: dict):
    if update:
        update = telebot.types.Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return

bot.remove_webhook()

bot.set_webhook(
    url=config['app-url']+f"/{token}/",
    certificate=open(config['ssl-cert'], 'r')
)

uvicorn.run(
    app,
    host="0.0.0.0",
    port=80,
    ssl_certfile=config['ssl-cert'],
    ssl_keyfile=config['ssl-private']
)
