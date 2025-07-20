import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from linebot.exceptions import InvalidSignatureError

load_dotenv()
app = Flask(__name__)

# โหลดค่าจาก .env
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
ARK_API_KEY = os.getenv("ARK_API_KEY")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ฟังก์ชันเรียก Seedream API
def generate_image(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ARK_API_KEY}",
    }
    data = {
        "model": "seedream-3-0-t2i-250415",
        "prompt": prompt,
        "response_format": "url",
        "size": "1080x1920",
        "guidance_scale": 3,
        "watermark": True
    }

    response = requests.post("https://ark.ap-southeast.bytepluses.com/api/v3/images/generations", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    else:
        return None

# รับ Webhook
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# รับข้อความจากแชท
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    if text.startswith("/create"):
        prompt = text.replace("/create", "", 1).strip()
        if not prompt:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="อาจจะยังพิพม์ไม่ถูกค่ะ ตัวอย่างที่ถูกเช่น /create แมวใส่หมวก"))
            return
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⏳ รอซักครูนะคะ Nirava กำลังสร้างภาพ..."))
        image_url = generate_image(prompt)
        if image_url:
            line_bot_api.push_message(event.source.user_id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
        else:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="เกิดปัญหาขัดข้อง Nirava ต้องขออภัยด้วยจริงๆค่ะ"))

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
