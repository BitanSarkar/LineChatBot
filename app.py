from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', 'abc'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', 'abc'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    got_message = event.message.text
    replyMessage = "echo: "+got_message
    if got_message == 'flight search':
        replyMessage = "You want to search a flight for oneway or round trip?"
    if got_message == 'round trip':
        replyMessage = "Round trip searches"
    if got_message == 'oneway' or got_message == 'one way' or got_message == 'one-way':
        replyMessage = "One way searches"
    line_bot_api.reply_message(event.reply_token,[TextSendMessage(text=replyMessage), TextSendMessage(text="do you want to book this flight")], timeout=5000)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)