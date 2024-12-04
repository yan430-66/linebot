from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
import os
import module1, module2, module3, module4, module5, module6

# 載入 .env 檔案中的環境變數
load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_BOT_API_KEY'))
handler = WebhookHandler(os.getenv('WEBHOOK_HANDLER_KEY'))

# 全局變數來存儲使用者的選擇狀態
user_state = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return jsonify({"status": "error", "message": "Invalid signature"}), 400

    return jsonify({"status": "success"}), 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text

    if user_id in user_state:
        # 使用者已選擇功能，等待下一則訊息
        module = user_state[user_id]
        reply = module.handle_message(user_message)
        del user_state[user_id]  # 清除狀態
    else:
        # 使用者選擇功能
        if user_message == "1":
            user_state[user_id] = module1
            reply = "請傳送一則訊息讓 module1 判斷。"
        elif user_message == "2":
            reply = module2.handle_message(user_message)
        elif user_message == "3":
            reply = module3.handle_message(user_message)
        elif user_message == "4":
            reply = module4.handle_message(user_message)
        elif user_message == "5":
            reply = module5.handle_message(user_message)
        elif user_message == "6":
            reply = module6.handle_message(user_message)
        else:
            reply = "請輸入有效的選項。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=8000)