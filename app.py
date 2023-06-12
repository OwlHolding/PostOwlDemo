import json
from aiohttp import web
import telebot
import ssl

from bot import bot

with open('ssl-config.json', 'rb') as file:
    ssl_config = json.load(file)

app = web.Application()


async def handler(request):
    request_body = await request.json()
    update = telebot.types.Update.de_json(request_body)
    bot.process_new_updates([update])

app.router.add_post("/", handler)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(ssl_config['ssl-cert'], ssl_config['ssl-private'])

web.run_app(
    app,
    host="0.0.0.0",
    port=80,
    ssl_context=context
)
