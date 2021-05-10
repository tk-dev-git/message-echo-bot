import os
from flask import Flask, request, abort
from flask_caching import Cache
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app=Flask(__name__)

# Cache 設定
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app)

# 環境変数の取得
CHANNEL_ACCESS_TOKEN=os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET=os.environ['CHANNEL_SECRET']
line_bot_api=LineBotApi(CHANNEL_ACCESS_TOKEN)
handler=WebhookHandler(CHANNEL_SECRET)

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # print('OS Environ: {}'.format(os.environ))
    body = request.get_data(as_text=True)
    print('Request body: {}'.format(body))

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('[TextMessage]: {}'.format(event))

    echo_text = event.message.text
    number = cache.get('session')
    if number is None or number == 0:
        number = 1
    else:
        number = number + 1
    echo_text = '{} - [No.{}]'.format(echo_text, number)
    cache.set("session", number)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=echo_text))


if __name__=="__main__":
    port = int(os.getenv("PORT",5000))
    app.run(host="0.0.0.0", port=port)
