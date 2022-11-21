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
    print("".join(["-"]*100))
    print(userData)
    print("".join(["-"]*100))
    got_message = event.message.text.lower().strip()
    user_id = event.source.user_id
    last_message_info = {}
    if user_id in userData:
        last_message_info = userData[user_id]
        if last_message_info["is_required"] and last_message_info["message"] == "Do you wish to travel somewhere?":
            if "yes" in got_message or "yup" in got_message:
                userData[user_id] = {
                    "message": "Where do you want to travel?",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Where do you want to travel?"))
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
        if last_message_info["is_required"] and last_message_info["message"] == "Where do you want to travel?":
            userData[user_id] = {
                "message": "When do you want to travel?",
                "place": got_message,
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"When do you want to travel to {got_message.capitalize()}?"))
        if last_message_info["is_required"] and last_message_info["message"] == "When do you want to travel?":
            userData[user_id] = {
                "message": "In which city are you right now?",
                "place": last_message_info["place"],
                "time": got_message,
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="In which city are you right now?"))
        if last_message_info["is_required"] and last_message_info["message"] == "In which city are you right now?":
            place = last_message_info["place"]
            time = last_message_info["time"]
            userData[user_id] = {
                "message": "Option Selection",
                "place": place,
                "time": time,
                "from_place": got_message,
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, messages=[TextSendMessage(text=f"Searching for flights from {got_message.capitalize()} to {place.capitalize()} on {time.capitalize()}"), TextSendMessage(text=f"These are your options,\n1. Flight ABC\n2. Flight DEF\n3. Flight GFHI\n4. Flight DErfF\n5. Flight GFHffI   \nSelect flight by clicking option [1 - 5]")])
        if last_message_info["is_required"] and last_message_info["message"] == "Option Selection":
            flight = ["Flight ABC", "Flight DEF", "Flight GFHI", "Flight DErfF", "Flight GFHffI"]
            place = last_message_info["place"]
            time = last_message_info["time"]
            from_place = last_message_info["from_place"]
            userData[user_id] = {
                "message": "confirmation",
                "place": place,
                "time": time,
                "from_place": from_place,
                "flight_search": flight[got_message-1],
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=f"Are you sure you want to book {flight[got_message-1]} from {got_message.capitalize()} to {place.capitalize()} on {time.capitalize()}?\n\n\n\nSeamless booking for you, as you are a valued SCB customer!"))
        if last_message_info["is_required"] and last_message_info["message"] == "confirmation":
            place = last_message_info["place"]
            time = last_message_info["time"]
            if "yes" in got_message or "yup" in got_message:
                userData[user_id] = {
                    "message": "Comfirm_yes",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="Confirming your booking! \U0001f610"), TextSendMessage(text="Your booking is confirmed! \U0001f60d, you confirmation id is HOIU3q4142oHOI, reservation ID is HH202299110"), TextSendMessage(text=f"Do you want to rent cars in {place.capitalize()} on {time}")])
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
    replyMessage = "Can't understand what you are trying to say! \U0001f615"
    if "hey" in got_message or "hello" in got_message  or "hi" in got_message :
        userData[user_id] = {
                "message": "Do you wish to travel somewhere?",
                "is_required": True
            }
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Do you wish to travel somewhere? \U0001f60d \n\n\nAssuming you want to travel single, if you want to add passenger, please type the count \nExample: yes 2 adult 1 child"))
    else:
        userData[user_id] = {
            "message": "",
            "is_required": False
        }
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replyMessage))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)