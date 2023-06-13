import json
from aiohttp import web
import telebot
import ssl

from bot import bot

with open('ssl-config.json', 'rb') as file:
    ssl_config = json.load(file)

app = web.Application()


async def handler(request):
    if request.match_info.get("token") == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post("/{token}/", handler)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(ssl_config['ssl-cert'], ssl_config['ssl-private'])

web.run_app(
    app,
    host="0.0.0.0",
    port=80,
    ssl_context=context
)
