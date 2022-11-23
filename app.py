from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction, FlexSendMessage
)

import string    
import random
import calendar
import datetime

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

@handler.add(PostbackEvent)
def handle_postback_action(event):
    print("".join(["-"]*100))
    print(userData)
    print("".join(["-"]*100))
    user_id = event.source.user_id
    last_message_info = {}
    if user_id in userData and userData[user_id]["is_required"]:
        last_message_info = userData[user_id]
        if last_message_info["is_required"] and last_message_info["message"] == "When do you want to travel?":
            date = event.postback.params["date"]
            date_time = datetime.datetime.strptime(date, '%Y-%m-%d')
            userData[user_id] = {
                "message": "In which city are you right now?",
                "place": last_message_info["place"],
                "time": date_time.date + " " + date_time.strftime("%B"),
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="In which city are you right now?"))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("".join(["-"]*100))
    print(userData)
    print("".join(["-"]*100))
    got_message = event.message.text.lower().strip()
    user_id = event.source.user_id
    last_message_info = {}
    if user_id in userData and userData[user_id]["is_required"]:
        last_message_info = userData[user_id]
        if last_message_info["is_required"] and last_message_info["message"] == "Do you wish to travel somewhere?":
            if "travel" in got_message and "flight" in got_message:
                userData[user_id] = {
                    "message": "Where do you want to travel?",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Where do you want to travel?"))
            else:
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
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='hello', contents={
                                                                                                        "type": "bubble",
                                                                                                        "body": {
                                                                                                            "type": "box",
                                                                                                            "layout": "vertical",
                                                                                                            "contents": [
                                                                                                            {
                                                                                                                "type": "text",
                                                                                                                "text": "When do you want to travel?"
                                                                                                            },
                                                                                                            {
                                                                                                                "type": "button",
                                                                                                                "action": {
                                                                                                                "type": "datetimepicker",
                                                                                                                "label": "Select a date",
                                                                                                                "data": "date",
                                                                                                                "mode": "date"
                                                                                                                },
                                                                                                                "color": "#33cc33",
                                                                                                                "position": "relative",
                                                                                                                "style": "primary",
                                                                                                                "flex": 0,
                                                                                                                "height": "sm",
                                                                                                                "offsetStart": "none",
                                                                                                                "gravity": "bottom",
                                                                                                                "margin": "md"
                                                                                                            }
                                                                                                            ]
                                                                                                        }
                                                                                                    }))
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
            line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=f"Searching for flights from {got_message.upper()} to {place.upper()} on {time.upper()}"), FlexSendMessage(
                                                                alt_text='hello',
                                                                contents={
                                                                        "type": "carousel",
                                                                        "contents": [
                                                                            {
                                                                            "type": "bubble",
                                                                            "body": {
                                                                                "type": "box",
                                                                                "layout": "vertical",
                                                                                "contents": [
                                                                                {
                                                                                    "type": "text",
                                                                                    "text": "Option 1",
                                                                                    "weight": "bold",
                                                                                    "style": "italic",
                                                                                    "decoration": "underline",
                                                                                    "align": "center"
                                                                                },
                                                                                {
                                                                                    "type": "image",
                                                                                    "url": "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.30+PM.jpeg",
                                                                                    "size": "full",
                                                                                    "action": {
                                                                                    "type": "message",
                                                                                    "label": "option 1",
                                                                                    "text": "1"
                                                                                    }
                                                                                }
                                                                                ],
                                                                                "flex": 0
                                                                            }
                                                                            },
                                                                            {
                                                                            "type": "bubble",
                                                                            "body": {
                                                                                "type": "box",
                                                                                "layout": "vertical",
                                                                                "contents": [
                                                                                {
                                                                                    "type": "text",
                                                                                    "text": "Option 2",
                                                                                    "weight": "bold",
                                                                                    "style": "italic",
                                                                                    "decoration": "underline",
                                                                                    "align": "center"
                                                                                },
                                                                                {
                                                                                    "type": "image",
                                                                                    "url": "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg",
                                                                                    "size": "full",
                                                                                    "action": {
                                                                                    "type": "message",
                                                                                    "label": "option 2",
                                                                                    "text": "2"
                                                                                    }
                                                                                }
                                                                                ]
                                                                            }
                                                                            },
                                                                            {
                                                                            "type": "bubble",
                                                                            "body": {
                                                                                "type": "box",
                                                                                "layout": "vertical",
                                                                                "contents": [
                                                                                {
                                                                                    "type": "text",
                                                                                    "text": "Option 3",
                                                                                    "weight": "bold",
                                                                                    "style": "italic",
                                                                                    "decoration": "underline",
                                                                                    "align": "center"
                                                                                },
                                                                                {
                                                                                    "type": "image",
                                                                                    "url": "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg",
                                                                                    "size": "full",
                                                                                    "action": {
                                                                                    "type": "message",
                                                                                    "label": "option 3",
                                                                                    "text": "3"
                                                                                    }
                                                                                }
                                                                                ]
                                                                            }
                                                                            },
                                                                            {
                                                                            "type": "bubble",
                                                                            "body": {
                                                                                "type": "box",
                                                                                "layout": "vertical",
                                                                                "contents": [
                                                                                {
                                                                                    "type": "text",
                                                                                    "text": "Option 4",
                                                                                    "weight": "bold",
                                                                                    "style": "italic",
                                                                                    "decoration": "underline",
                                                                                    "align": "center"
                                                                                },
                                                                                {
                                                                                    "type": "image",
                                                                                    "url": "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.30+PM.jpeg",
                                                                                    "size": "full",
                                                                                    "action": {
                                                                                    "type": "message",
                                                                                    "label": "option 4",
                                                                                    "text": "4"
                                                                                    }
                                                                                }
                                                                                ]
                                                                            }
                                                                            },
                                                                            {
                                                                            "type": "bubble",
                                                                            "body": {
                                                                                "type": "box",
                                                                                "layout": "vertical",
                                                                                "contents": [
                                                                                {
                                                                                    "type": "text",
                                                                                    "text": "Option 5",
                                                                                    "weight": "bold",
                                                                                    "style": "italic",
                                                                                    "decoration": "underline",
                                                                                    "align": "center"
                                                                                },
                                                                                {
                                                                                    "type": "image",
                                                                                    "url": "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg",
                                                                                    "size": "full",
                                                                                    "action": {
                                                                                    "type": "message",
                                                                                    "label": "option 5",
                                                                                    "text": "5"
                                                                                    }
                                                                                }
                                                                                ]
                                                                            }
                                                                            }
                                                                        ]
                                                                        }
                                                            )])
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
                "flight_search": flight[int(got_message)-1],
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, messages=TextSendMessage(text=f"Are you sure you want to book this flight from {from_place.upper()} to {place.upper()}?\n\n\n\nSeamless booking for you, as you are a valued SCB customer!"))
        if last_message_info["is_required"] and last_message_info["message"] == "confirmation":
            place = last_message_info["place"]
            time = last_message_info["time"]
            if "yes" in got_message or "yup" in got_message:
                userData[user_id] = {
                    "message": "Comfirm_yes",
                    "place": place,
                    "time": time,
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="Confirming your booking! \U0001f610"), TextSendMessage(text=f"Your booking is confirmed! \U0001f60d, you confirmation ID is {''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)) }, reservation ID is {''.join(random.choices(string.ascii_uppercase + string.digits, k = 5)) }"), TextSendMessage(text=f"Where are you going to stay in {place.upper()} on {time}? Do you want to check out amazing hotels in {place.upper()}"), FlexSendMessage(
                                                                alt_text='hello',
                                                                contents={
                                                                            "type": "carousel",
                                                                            "contents": [
                                                                                {
                                                                                "type": "bubble",
                                                                                "body": {
                                                                                    "type": "box",
                                                                                    "layout": "vertical",
                                                                                    "contents": [
                                                                                    {
                                                                                        "type": "text",
                                                                                        "text": "Offers free delivery \U0001f60d",
                                                                                        "size": "md",
                                                                                        "weight": "bold",
                                                                                        "style": "italic"
                                                                                    },
                                                                                    {
                                                                                        "type": "image",
                                                                                        "url": "https://akhil9811bucket.s3.amazonaws.com/hotel/WhatsApp+Image+2022-11-22+at+12.59.20+PM.jpeg",
                                                                                        "size": "full",
                                                                                        "action": {
                                                                                        "type": "message",
                                                                                        "label": "action",
                                                                                        "text": "Avani Atrium Bangkok"
                                                                                        }
                                                                                    }
                                                                                    ],
                                                                                    "flex": 0
                                                                                }
                                                                                },
                                                                                {
                                                                                "type": "bubble",
                                                                                "body": {
                                                                                    "type": "box",
                                                                                    "layout": "vertical",
                                                                                    "contents": [
                                                                                    {
                                                                                        "type": "text",
                                                                                        "text": "Offers free delivery \U0001f60d",
                                                                                        "size": "md",
                                                                                        "weight": "bold",
                                                                                        "style": "italic"
                                                                                    },
                                                                                    {
                                                                                        "type": "image",
                                                                                        "url": "https://akhil9811bucket.s3.amazonaws.com/hotel/WhatsApp+Image+2022-11-22+at+12.59.35+PM.jpeg",
                                                                                        "size": "full",
                                                                                        "action": {
                                                                                        "type": "message",
                                                                                        "label": "action",
                                                                                        "text": "Column Bangkok"
                                                                                        }
                                                                                    }
                                                                                    ]
                                                                                }
                                                                                }
                                                                            ]
                                                                            }
                                                            )])
            else:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
        if last_message_info["is_required"] and last_message_info["message"] == "Comfirm_yes":
            place = last_message_info["place"]
            time = last_message_info["time"]
            if "avani atrium bangkok" == got_message or "column bangkok" == got_message:
                userData[user_id] = {
                    "message": "cars_check",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Looking for reservations in {got_message.capitalize()} on {time.upper()} in {place.upper()}"))
            else:
                userData[user_id] = {
                    "message": "hotel_check",
                    "place": place,
                    "time": time,
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Do you want to rent some cars in {place.upper()} on {time}"))
        if last_message_info["is_required"] and last_message_info["message"] == "hotel_check":
            place = last_message_info["place"]
            time = last_message_info["time"]
            if "yes" in got_message or "yup" in got_message:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Looking for cars on {time.upper()} in {place.upper()}"))
            else:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
    else:
        if "hey" in got_message or "hello" in got_message  or "hi" in got_message :
            userData[user_id] = {
                    "message": "Do you wish to travel somewhere?",
                    "is_required": True
                }
            line_bot_api.reply_message(event.reply_token, [FlexSendMessage(
                                                                alt_text='hello',
                                                                contents={
                                                                    "type": "bubble",
                                                                    "body": {
                                                                        "type": "box",
                                                                        "layout": "vertical",
                                                                        "contents": [
                                                                        {
                                                                            "type": "text",
                                                                            "text": "Hey, I am BookEazie. I am your personal tour guide, making your bookings easy.",
                                                                            "wrap": True,
                                                                            "contents": [
                                                                            {
                                                                                "type": "span",
                                                                                "text": "Hey, I am "
                                                                            },
                                                                            {
                                                                                "type": "span",
                                                                                "text": "BookEazie",
                                                                                "weight": "bold",
                                                                                "decoration": "none",
                                                                                "style": "italic",
                                                                                "color": "#49be25"
                                                                            },
                                                                            {
                                                                                "type": "span",
                                                                                "text": ". I am your "
                                                                            },
                                                                            {
                                                                                "type": "span",
                                                                                "text": "personal AI tour guide",
                                                                                "weight": "bold"
                                                                            },
                                                                            {
                                                                                "type": "span",
                                                                                "text": ", making your travel bookings easy."
                                                                            }
                                                                            ]
                                                                        },
                                                                        {
                                                                            "type": "separator",
                                                                            "margin": "lg"
                                                                        },
                                                                        {
                                                                            "type": "text",
                                                                            "text": "I provide bookings and reservations, from flight to hotel, from renting cars to reserving seats in restaurants.",
                                                                            "wrap": True
                                                                        },
                                                                        {
                                                                            "type": "separator",
                                                                            "margin": "lg"
                                                                        },
                                                                        {
                                                                            "type": "text",
                                                                            "text": "Type down what do you want to do! And I am there for you!",
                                                                            "wrap": True,
                                                                            "align": "center",
                                                                            "style": "italic",
                                                                            "size": "lg"
                                                                        }
                                                                        ],
                                                                        "justifyContent": "space-around"
                                                                    }
                                                                    }
                                                            )])
        else:
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Can't understand what you are trying to say! \U0001f615"))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)