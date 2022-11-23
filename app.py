from flask import Flask, request, abort
import speech_recognition as sr
from pydub import AudioSegment
recognizer = sr.Recognizer()

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage, AudioMessage, FlexSendMessage
)

import string    
import random
import calendar
import datetime
import re
import wave
import struct, aifc
import numpy as np

rate = 44100

import os
AudioSegment.converter = os.path.dirname(os.path.abspath(__file__)) + "\\vendor\\ffmpeg\\ffmpeg.exe"
AudioSegment.ffmpeg = os.path.dirname(os.path.abspath(__file__)) + "\\vendor\\ffmpeg\\ffmpeg.exe"
AudioSegment.ffprobe = os.path.dirname(os.path.abspath(__file__)) + "\\vendor\\ffmpeg\\ffprobe.exe"

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
    print(event)
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
                "time": str(date_time.day) + " " + str(date_time.strftime("%B")),
                "is_required": True
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="In which city are you right now?"))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("".join(["-"]*100))
    print(event)
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
                                                                                                                "text": f"When do you want to travel to {got_message}?",
                                                                                                                "wrap": True,
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
            flight = ["https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.30+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.30+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg"]
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
            line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage( alt_text=f"Are you sure you want to book this flight from {from_place.upper()} to {place.upper()}?\n\n\n\nSeamless booking for you, as you are a valued SCB customer!",
                                                                                    contents={
                                                                                                "type": "bubble",
                                                                                                "hero": {
                                                                                                    "type": "image",
                                                                                                    "url": flight[int(got_message)-1],
                                                                                                    "size": "full"
                                                                                                },
                                                                                                "body": {
                                                                                                    "type": "box",
                                                                                                    "layout": "vertical",
                                                                                                    "contents": [
                                                                                                    {
                                                                                                        "type": "button",
                                                                                                        "action": {
                                                                                                        "type": "uri",
                                                                                                        "label": "Continue booking here",
                                                                                                        "uri": "http://webpages-hack.s3-website-us-east-1.amazonaws.com/",
                                                                                                        "altUri": {
                                                                                                            "desktop": "http://webpages-hack.s3-website-us-east-1.amazonaws.com/"
                                                                                                        }
                                                                                                        },
                                                                                                        "height": "md",
                                                                                                        "style": "primary",
                                                                                                        "color": "#009933",
                                                                                                        "gravity": "center"
                                                                                                    },
                                                                                                    {
                                                                                                        "type": "button",
                                                                                                        "action": {
                                                                                                        "type": "uri",
                                                                                                        "label": "Continue booking through App",
                                                                                                        "uri": "https://play.google.com/store/apps/details?id=th.in.robinhood&hl=en_US&gl=US",
                                                                                                        "altUri": {
                                                                                                            "desktop": "https://play.google.com/store/apps/details?id=th.in.robinhood&hl=en_US&gl=US"
                                                                                                        }
                                                                                                        },
                                                                                                        "style": "primary",
                                                                                                        "color": "#a300cc",
                                                                                                        "margin": "lg",
                                                                                                        "position": "relative",
                                                                                                        "gravity": "center"
                                                                                                    }
                                                                                                    ]
                                                                                                }
                                                                                            }))
        if last_message_info["is_required"] and last_message_info["message"] == "confirmation":
            place = last_message_info["place"]
            time = last_message_info["time"]
            if "check" in got_message and "status" in got_message and "last" in got_message:
                userData[user_id] = {
                    "message": "Comfirm_yes",
                    "place": place,
                    "time": time,
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=f"Your booking was confirmed! \U0001f60d, you confirmation ID is {''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)) }, reservation ID is {''.join(random.choices(string.ascii_uppercase + string.digits, k = 5)) }"), TextSendMessage(text=f"Where are you going to stay in {place.upper()} on {time}? Do you want to check out amazing hotels in {place.upper()}"), FlexSendMessage(
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
                    "message": "feedback_time",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"),
                                                                                                        FlexSendMessage(alt_text="feedback", contents={
                                                                                                                                                        "type": "bubble",
                                                                                                                                                        "body": {
                                                                                                                                                            "type": "box",
                                                                                                                                                            "layout": "horizontal",
                                                                                                                                                            "contents": [
                                                                                                                                                            {
                                                                                                                                                                "type": "image",
                                                                                                                                                                "url": "https://i.ibb.co/Xy109LY/final-i-guess.png"
                                                                                                                                                            },
                                                                                                                                                            {
                                                                                                                                                                "type": "text",
                                                                                                                                                                "text": "Did you like me? Rate me out of 10, and give some feedback!",
                                                                                                                                                                "wrap": True,
                                                                                                                                                                "weight": "bold",
                                                                                                                                                                "style": "italic"
                                                                                                                                                            }
                                                                                                                                                            ]
                                                                                                                                                        }
                                                                                                                                                        })])
        if last_message_info["is_required"] and last_message_info["message"] == "Booking list finder":
            choice = [int(s) for s in re.findall(r'-?\d+\.?\d*', got_message)][0]
            image_url = ["https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hotel/WhatsApp+Image+2022-11-22+at+12.59.20+PM.jpeg"]
            bookingIds = ["booking ID GUYU98983", "booking ID FFY348383","reservation ID YUI698HLL"]
            if "view" in got_message or "details" in got_message:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="abc", contents={
                                                                                                            "type": "bubble",
                                                                                                            "body": {
                                                                                                                "type": "box",
                                                                                                                "layout": "vertical",
                                                                                                                "contents": [
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "Here is the booking you are looking for! \U0001f604",
                                                                                                                    "wrap": True,
                                                                                                                    "weight": "bold"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "image",
                                                                                                                    "url": image_url[choice-1],
                                                                                                                    "align": "center",
                                                                                                                    "gravity": "center",
                                                                                                                    "size": "full",
                                                                                                                    "margin": "none",
                                                                                                                    "position": "relative",
                                                                                                                    "aspectMode": "fit"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "contents": [
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": "Your "
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": bookingIds[choice-1],
                                                                                                                        "weight": "bold",
                                                                                                                        "style": "italic"
                                                                                                                    }
                                                                                                                    ],
                                                                                                                    "wrap": True
                                                                                                                }
                                                                                                                ]
                                                                                                            }
                                                                                                        }))
            elif "cancel" in got_message:
                userData[user_id] = {
                    "message": "cancel_confirm",
                    "choice": choice,
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="abc", contents={
                                                                                                            "type": "bubble",
                                                                                                            "body": {
                                                                                                                "type": "box",
                                                                                                                "layout": "vertical",
                                                                                                                "contents": [
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "Are you sure you want to cancel? Cancellation charges may apply! \U0001f97a",
                                                                                                                    "wrap": True,
                                                                                                                    "weight": "bold"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "image",
                                                                                                                    "url": image_url[choice-1],
                                                                                                                    "align": "center",
                                                                                                                    "gravity": "center",
                                                                                                                    "size": "full",
                                                                                                                    "margin": "none",
                                                                                                                    "position": "relative",
                                                                                                                    "aspectMode": "fit"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "contents": [
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": "Your "
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": bookingIds[choice-1],
                                                                                                                        "weight": "bold",
                                                                                                                        "style": "italic"
                                                                                                                    }
                                                                                                                    ],
                                                                                                                    "wrap": True
                                                                                                                }
                                                                                                                ]
                                                                                                            }
                                                                                                        }))
            else:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
        if last_message_info["is_required"] and last_message_info["message"] == "cancel_confirm":
            choice = last_message_info["choice"]
            image_url = ["https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hotel/WhatsApp+Image+2022-11-22+at+12.59.20+PM.jpeg"]
            bookingIds = ["booking ID GUYU98983", "booking ID FFY348383","reservation ID YUI698HLL"]
            if "yes" in got_message or "yup" in got_message:
                userData[user_id] = {
                    "message": "feedback_time",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [FlexSendMessage(alt_text="abc", contents={
                                                                                                            "type": "bubble",
                                                                                                            "body": {
                                                                                                                "type": "box",
                                                                                                                "layout": "vertical",
                                                                                                                "contents": [
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "A ticket has been raise for the cancellation of this booking! \U0001fae4",
                                                                                                                    "wrap": True,
                                                                                                                    "weight": "bold"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "image",
                                                                                                                    "url": image_url[choice-1],
                                                                                                                    "align": "center",
                                                                                                                    "gravity": "center",
                                                                                                                    "size": "full",
                                                                                                                    "margin": "none",
                                                                                                                    "position": "relative",
                                                                                                                    "aspectMode": "fit"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "contents": [
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": "Your "
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": bookingIds[choice-1],
                                                                                                                        "weight": "bold",
                                                                                                                        "style": "italic"
                                                                                                                    }
                                                                                                                    ],
                                                                                                                    "wrap": True
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "\n\n\n\n*Any further communication would be done through your registered email or phone number! ",
                                                                                                                    "wrap": True,
                                                                                                                    "size": "xs"
                                                                                                                }
                                                                                                                ]
                                                                                                            }
                                                                                                        }),
                                                                                                        FlexSendMessage(alt_text="feedback", contents={
                                                                                                                                                        "type": "bubble",
                                                                                                                                                        "body": {
                                                                                                                                                            "type": "box",
                                                                                                                                                            "layout": "horizontal",
                                                                                                                                                            "contents": [
                                                                                                                                                            {
                                                                                                                                                                "type": "image",
                                                                                                                                                                "url": "https://i.ibb.co/Xy109LY/final-i-guess.png"
                                                                                                                                                            },
                                                                                                                                                            {
                                                                                                                                                                "type": "text",
                                                                                                                                                                "text": "Did you like me? Rate me out of 10, and give some feedback!",
                                                                                                                                                                "wrap": True,
                                                                                                                                                                "weight": "bold",
                                                                                                                                                                "style": "italic"
                                                                                                                                                            }
                                                                                                                                                            ]
                                                                                                                                                        }
                                                                                                                                                        })])
            else:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
        if last_message_info["is_required"] and last_message_info["message"] == "feedback_time":
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Thank you for your feedback \U0001f9e1 \U0001f9e1 \U0001f9e1"))

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
        elif "list" in got_message:
            userData[user_id] = {
                    "message": "Booking list finder",
                    "is_required": True
                }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Here are your bookings\n1. Bangkok Airways 30th November booking ID GUYU98983\n2. Thai Smile 12th December booking ID FFY348383\n3. Hotel Avani Atrium Bangkok 15th December reservation ID YUI698HLL"))
        else:
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Can't understand what you are trying to say! \U0001f615"))

def output_wave(path, frames):
    # Python 3.X allows the use of the with statement
    # with wave.open(path,'w') as output:
    #     # Set parameters for output WAV file
    #     output.setparams((2,2,rate,0,'NONE','not compressed'))
    #     output.writeframes(frames)

    output = wave.open(path,'w')
    output.setparams((1,2,rate,0,'NONE','not compressed'))
    output.writeframes(frames)
    output.close()

@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    print("".join(["-"]*100))
    print(event)
    print("".join(["-"]*100))
    print(userData)
    print("".join(["-"]*100))
    user_id = event.source.user_id
    message_content = line_bot_api.get_message_content(event.message.id)
    print(message_content.content)
    path1 = os.path.dirname(os.path.abspath(__file__))+"\\"+str(user_id)+".m4a"
    path2 = os.path.dirname(os.path.abspath(__file__)+"\\"+str(user_id))+".wav"
    fd = open(path1, 'wb')
    for chunk in message_content.iter_content():
        fd.write(chunk)
    fd.close()
    sound = AudioSegment.from_file(path1,format="m4a")
    sound.export(path2, format="wav")
    rec = sr.AudioFile(path2)
    got_message = ""
    with rec as source:
        audio = recognizer.record(source)
        try:
            got_message = recognizer.recognize_google(audio)
            print(got_message)
        except sr.RequestError as e:  
            print("error; {0}".format(e))
        except Exception as e:
            print (e)
        print(got_message)
    got_message = ""
    print(got_message)
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
                                                                                                                "text": f"When do you want to travel to {got_message}?",
                                                                                                                "wrap": True,
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
            flight = ["https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.30+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.30+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg"]
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
            line_bot_api.reply_message(event.reply_token, messages=FlexSendMessage( alt_text=f"Are you sure you want to book this flight from {from_place.upper()} to {place.upper()}?\n\n\n\nSeamless booking for you, as you are a valued SCB customer!",
                                                                                    contents={
                                                                                                "type": "bubble",
                                                                                                "hero": {
                                                                                                    "type": "image",
                                                                                                    "url": flight[int(got_message)-1],
                                                                                                    "size": "full"
                                                                                                },
                                                                                                "body": {
                                                                                                    "type": "box",
                                                                                                    "layout": "vertical",
                                                                                                    "contents": [
                                                                                                    {
                                                                                                        "type": "button",
                                                                                                        "action": {
                                                                                                        "type": "uri",
                                                                                                        "label": "Continue booking here",
                                                                                                        "uri": "https://flights.booking.com/checkout/pax/d7699_H4sIAAAAAAAA_y2Pa2-CMBSGf41-o9BSQU2ahdsW51CjbOqnBmq5OGcX2mTIr98ZLG3P85w3zUlObcy3Xtp2eWuq2miruaNKGVXlRiKhvuyyhVIo9dncKztvWjtcr6PNidA4iVwMxca2BUcsz0-yM5ZuBZs2hUS5Fgwf_rVlHiJxfApfss0QCWUYRWTrekkYHP14CC8sjX66bR_oNNbdB7zsqh9prx9Zn5L9-2uYJQ4evkoB0xGi_mLsVa4ZHU0YRpxRL4bt3w67aDe2hvmUONQduo5hgn1nquVNCtOo-1o-2HPsUuJbsJ0UhFgrPgRzCzYdgmRCIuyRa10UYBM3gFtxBznAGoiBOT8dEXbOoAVf_EHwYAa4cG8hcZmDSu7P5piClZwmgIZjNI658tUR0PObkyvh_gJwtOp_oAEAAA../52588edf926412b959f9af56ff4a1cc5c9638ad94dab8f11e0f6c0963b32ee2c6c4de080d309c8d627b18f544f79ecf849c609bda5a6c41e38ca5658f9c70c06271dc9c6adcf86e3f645df165f3c786703b9cd038b9d15a51701?aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYAQm4ARfIAQzYAQHoAQH4AQuIAgGoAgO4Aqfg95sGwAIB0gIkNTg5MmE5ZTAtZTI3Ni00YWExLWJkZjItZmFiNTVlZTE1NTM12AIG4AIB",
                                                                                                        "altUri": {
                                                                                                            "desktop": "https://flights.booking.com/checkout/pax/d7699_H4sIAAAAAAAA_y2Pa2-CMBSGf41-o9BSQU2ahdsW51CjbOqnBmq5OGcX2mTIr98ZLG3P85w3zUlObcy3Xtp2eWuq2miruaNKGVXlRiKhvuyyhVIo9dncKztvWjtcr6PNidA4iVwMxca2BUcsz0-yM5ZuBZs2hUS5Fgwf_rVlHiJxfApfss0QCWUYRWTrekkYHP14CC8sjX66bR_oNNbdB7zsqh9prx9Zn5L9-2uYJQ4evkoB0xGi_mLsVa4ZHU0YRpxRL4bt3w67aDe2hvmUONQduo5hgn1nquVNCtOo-1o-2HPsUuJbsJ0UhFgrPgRzCzYdgmRCIuyRa10UYBM3gFtxBznAGoiBOT8dEXbOoAVf_EHwYAa4cG8hcZmDSu7P5piClZwmgIZjNI658tUR0PObkyvh_gJwtOp_oAEAAA../52588edf926412b959f9af56ff4a1cc5c9638ad94dab8f11e0f6c0963b32ee2c6c4de080d309c8d627b18f544f79ecf849c609bda5a6c41e38ca5658f9c70c06271dc9c6adcf86e3f645df165f3c786703b9cd038b9d15a51701?aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYAQm4ARfIAQzYAQHoAQH4AQuIAgGoAgO4Aqfg95sGwAIB0gIkNTg5MmE5ZTAtZTI3Ni00YWExLWJkZjItZmFiNTVlZTE1NTM12AIG4AIB"
                                                                                                        }
                                                                                                        },
                                                                                                        "height": "md",
                                                                                                        "style": "primary",
                                                                                                        "color": "#009933",
                                                                                                        "gravity": "center"
                                                                                                    },
                                                                                                    {
                                                                                                        "type": "button",
                                                                                                        "action": {
                                                                                                        "type": "uri",
                                                                                                        "label": "Continue booking through App",
                                                                                                        "uri": "https://play.google.com/store/apps/details?id=th.in.robinhood&hl=en_US&gl=US",
                                                                                                        "altUri": {
                                                                                                            "desktop": "https://play.google.com/store/apps/details?id=th.in.robinhood&hl=en_US&gl=US"
                                                                                                        }
                                                                                                        },
                                                                                                        "style": "primary",
                                                                                                        "color": "#a300cc",
                                                                                                        "margin": "lg",
                                                                                                        "position": "relative",
                                                                                                        "gravity": "center"
                                                                                                    }
                                                                                                    ]
                                                                                                }
                                                                                            }))
        if last_message_info["is_required"] and last_message_info["message"] == "confirmation":
            place = last_message_info["place"]
            time = last_message_info["time"]
            if "check" in got_message and "status" in got_message and "last" in got_message:
                userData[user_id] = {
                    "message": "Comfirm_yes",
                    "place": place,
                    "time": time,
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=f"Your booking was confirmed! \U0001f60d, you confirmation ID is {''.join(random.choices(string.ascii_uppercase + string.digits, k = 10)) }, reservation ID is {''.join(random.choices(string.ascii_uppercase + string.digits, k = 5)) }"), TextSendMessage(text=f"Where are you going to stay in {place.upper()} on {time}? Do you want to check out amazing hotels in {place.upper()}"), FlexSendMessage(
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
                    "message": "feedback_time",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"),
                                                                                                        FlexSendMessage(alt_text="feedback", contents={
                                                                                                                                                        "type": "bubble",
                                                                                                                                                        "body": {
                                                                                                                                                            "type": "box",
                                                                                                                                                            "layout": "horizontal",
                                                                                                                                                            "contents": [
                                                                                                                                                            {
                                                                                                                                                                "type": "image",
                                                                                                                                                                "url": "https://i.ibb.co/Xy109LY/final-i-guess.png"
                                                                                                                                                            },
                                                                                                                                                            {
                                                                                                                                                                "type": "text",
                                                                                                                                                                "text": "Did you like me? Rate me out of 10, and give some feedback!",
                                                                                                                                                                "wrap": True,
                                                                                                                                                                "weight": "bold",
                                                                                                                                                                "style": "italic"
                                                                                                                                                            }
                                                                                                                                                            ]
                                                                                                                                                        }
                                                                                                                                                        })])
        if last_message_info["is_required"] and last_message_info["message"] == "Booking list finder":
            choice = [int(s) for s in re.findall(r'-?\d+\.?\d*', got_message)][0]
            image_url = ["https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hotel/WhatsApp+Image+2022-11-22+at+12.59.20+PM.jpeg"]
            bookingIds = ["booking ID GUYU98983", "booking ID FFY348383","reservation ID YUI698HLL"]
            if "view" in got_message or "details" in got_message:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="abc", contents={
                                                                                                            "type": "bubble",
                                                                                                            "body": {
                                                                                                                "type": "box",
                                                                                                                "layout": "vertical",
                                                                                                                "contents": [
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "Here is the booking you are looking for! \U0001f604",
                                                                                                                    "wrap": True,
                                                                                                                    "weight": "bold"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "image",
                                                                                                                    "url": image_url[choice-1],
                                                                                                                    "align": "center",
                                                                                                                    "gravity": "center",
                                                                                                                    "size": "full",
                                                                                                                    "margin": "none",
                                                                                                                    "position": "relative",
                                                                                                                    "aspectMode": "fit"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "contents": [
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": "Your "
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": bookingIds[choice-1],
                                                                                                                        "weight": "bold",
                                                                                                                        "style": "italic"
                                                                                                                    }
                                                                                                                    ],
                                                                                                                    "wrap": True
                                                                                                                }
                                                                                                                ]
                                                                                                            }
                                                                                                        }))
            elif "cancel" in got_message:
                userData[user_id] = {
                    "message": "cancel_confirm",
                    "choice": choice,
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="abc", contents={
                                                                                                            "type": "bubble",
                                                                                                            "body": {
                                                                                                                "type": "box",
                                                                                                                "layout": "vertical",
                                                                                                                "contents": [
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "Are you sure you want to cancel? Cancellation charges may apply! \U0001f97a",
                                                                                                                    "wrap": True,
                                                                                                                    "weight": "bold"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "image",
                                                                                                                    "url": image_url[choice-1],
                                                                                                                    "align": "center",
                                                                                                                    "gravity": "center",
                                                                                                                    "size": "full",
                                                                                                                    "margin": "none",
                                                                                                                    "position": "relative",
                                                                                                                    "aspectMode": "fit"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "contents": [
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": "Your "
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": bookingIds[choice-1],
                                                                                                                        "weight": "bold",
                                                                                                                        "style": "italic"
                                                                                                                    }
                                                                                                                    ],
                                                                                                                    "wrap": True
                                                                                                                }
                                                                                                                ]
                                                                                                            }
                                                                                                        }))
            else:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
        if last_message_info["is_required"] and last_message_info["message"] == "cancel_confirm":
            choice = last_message_info["choice"]
            image_url = ["https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.06.48+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hack/WhatsApp+Image+2022-11-22+at+12.08.50+PM.jpeg", "https://akhil9811bucket.s3.amazonaws.com/hotel/WhatsApp+Image+2022-11-22+at+12.59.20+PM.jpeg"]
            bookingIds = ["booking ID GUYU98983", "booking ID FFY348383","reservation ID YUI698HLL"]
            if "yes" in got_message or "yup" in got_message:
                userData[user_id] = {
                    "message": "feedback_time",
                    "is_required": True
                }
                line_bot_api.reply_message(event.reply_token, [FlexSendMessage(alt_text="abc", contents={
                                                                                                            "type": "bubble",
                                                                                                            "body": {
                                                                                                                "type": "box",
                                                                                                                "layout": "vertical",
                                                                                                                "contents": [
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "A ticket has been raise for the cancellation of this booking! \U0001fae4",
                                                                                                                    "wrap": True,
                                                                                                                    "weight": "bold"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "image",
                                                                                                                    "url": image_url[choice-1],
                                                                                                                    "align": "center",
                                                                                                                    "gravity": "center",
                                                                                                                    "size": "full",
                                                                                                                    "margin": "none",
                                                                                                                    "position": "relative",
                                                                                                                    "aspectMode": "fit"
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "contents": [
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": "Your "
                                                                                                                    },
                                                                                                                    {
                                                                                                                        "type": "span",
                                                                                                                        "text": bookingIds[choice-1],
                                                                                                                        "weight": "bold",
                                                                                                                        "style": "italic"
                                                                                                                    }
                                                                                                                    ],
                                                                                                                    "wrap": True
                                                                                                                },
                                                                                                                {
                                                                                                                    "type": "text",
                                                                                                                    "text": "\n\n\n\n*Any further communication would be done through your registered email or phone number! ",
                                                                                                                    "wrap": True,
                                                                                                                    "size": "xs"
                                                                                                                }
                                                                                                                ]
                                                                                                            }
                                                                                                        }),
                                                                                                        FlexSendMessage(alt_text="feedback", contents={
                                                                                                                                                        "type": "bubble",
                                                                                                                                                        "body": {
                                                                                                                                                            "type": "box",
                                                                                                                                                            "layout": "horizontal",
                                                                                                                                                            "contents": [
                                                                                                                                                            {
                                                                                                                                                                "type": "image",
                                                                                                                                                                "url": "https://i.ibb.co/Xy109LY/final-i-guess.png"
                                                                                                                                                            },
                                                                                                                                                            {
                                                                                                                                                                "type": "text",
                                                                                                                                                                "text": "Did you like me? Rate me out of 10, and give some feedback!",
                                                                                                                                                                "wrap": True,
                                                                                                                                                                "weight": "bold",
                                                                                                                                                                "style": "italic"
                                                                                                                                                            }
                                                                                                                                                            ]
                                                                                                                                                        }
                                                                                                                                                        })])
            else:
                userData[user_id] = {
                    "message": "",
                    "is_required": False
                }
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="No worries! \U0001f607 Just type \"Hey\", \"Hello\", \"Hi\" and start booking with us!!! \U0001fae0"))
        if last_message_info["is_required"] and last_message_info["message"] == "feedback_time":
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Thank you for your feedback \U0001f9e1 \U0001f9e1 \U0001f9e1"))
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
        elif "list" in got_message:
            userData[user_id] = {
                    "message": "Booking list finder",
                    "is_required": True
                }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Here are your bookings\n1. Bangkok Airways 30th November booking ID GUYU98983\n2. Thai Smile 12th December booking ID FFY348383\n3. Hotel Avani Atrium Bangkok 15th December reservation ID YUI698HLL"))
        else:
            userData[user_id] = {
                "message": "",
                "is_required": False
            }
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Can't understand what you are trying to say! \U0001f615"))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)