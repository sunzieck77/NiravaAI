from flask import Flask, request, abort
from linebot.v3.webhooks import WebhookHandler, MessageEvent, TextMessageContent
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage

import os

app = Flask(__name__)

# 🟡 ใช้ ENV สำหรับความปลอดภัย
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 🛡️ ตรวจสอบตัวแปร
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise ValueError("Environment variables LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set.")

# 🟢 ตั้งค่า Messaging API Client
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

# 🟢 Handler สำหรับ Webhook
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("❌ ERROR:", e)
        abort(400)
    return 'OK'


# ✅ ตอบกลับข้อความเมื่อมีคนส่งมา
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        user_message = event.message.text
        reply_token = event.reply_token

        # ตัวอย่างการตอบข้อความกลับ
        response_text = f"คุณพิมพ์ว่า: {user_message}"
        line_bot_api.reply_message(
            reply_token,
            [
                TextMessage(text=response_text)
            ]
        )

    except Exception as e:
        print("❌ Internal error:", e)

        # หากต้องการส่ง push กลับหาผู้ใช้
        try:
            line_bot_api.push_message(
                to=event.source.user_id,
                messages=[TextMessage(text="❌ เกิดข้อผิดพลาด ลองใหม่อีกครั้งนะคะ")]
            )
        except:
            print("⚠️ ไม่สามารถส่ง push message ได้")


if __name__ == "__main__":
    app.run()
