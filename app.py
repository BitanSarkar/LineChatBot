from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction
)

import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', 'abc'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET', 'abc'))

userData = {}

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

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     got_message = event.message.text
#     replyMessage = "echo: "+got_message
#     if got_message == 'flight search':
#         replyMessage = "You want to search a flight for oneway or round trip?"
#     if got_message == 'round trip':
#         replyMessage = "Round trip searches"
#     if got_message == 'oneway' or got_message == 'one way' or got_message == 'one-way':
#         replyMessage = "One way searches"
#     line_bot_api.reply_message(event.reply_token,TemplateSendMessage(
#         alt_text='Buttons template',
#         template=ButtonsTemplate(
#             thumbnail_image_url='https://example.com/image.jpg',
#             title='Menu',
#             text='Please select',
#             actions=[
#                 PostbackAction(
#                     label='postback',
#                     display_text='postback text',
#                     data='action=buy&itemid=1'            ),
#                 MessageAction(
#                     label='message',
#                     text='message text'
#                 ),
#                 URIAction(
#                     label='uri',
#                     uri='http://example.com/'
#                 )
#             ]
#         )
#     ), timeout=5000)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    got_message = event.message.text.lower()
    print(event.source)
    user_id = event.source["userId"]
    last_message_info = {}
    if user_id in userData:
        last_message_info = userData[user_id]
    if last_message_info["is_required"] and last_message_info["Do you wish to travel somewhere?"]:
        if "yes" in got_message or "yup" in got_message:
            userData[user_id] = {
                "last_message_info": "Where do you want to travel?",
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Where do you want to travel?"))
    if last_message_info["is_required"] and last_message_info["Where do you want to travel?"]:
        if "yes" in got_message or "yup" in got_message:
            userData[user_id] = {
                "last_message_info": "Where do you want to travel?",
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Where do you want to travel?"))
    replyMessage = "Can't understand what you are trying to say! \U0001f615"
    if "hey" in got_message or "hello" in got_message  or "hi" in got_message :
        if "flight" in got_message or "search" in got_message:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="So you are search for flights?"))
        if "flight" in got_message or "search" in got_message:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="So you are search for flights?"))
        userData[user_id] = {
                "last_message_info": "Do you wish to travel somewhere?",
                "is_required": True
            }
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Do you wish to travel somewhere? \U0001f60d"))
    if "flight" in got_message or "search" in got_message:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="So you are search for flights?"))
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replyMessage))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)