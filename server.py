import os
import uvicorn
import requests
import subprocess
import threading
import gradio as gr
from webui import webui
from src import CommandAnalyze
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

C = {
    'green': '\033[92m',
    'red': '\033[91m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'black': '\033[30m',
    'grey': '\033[90m',
    'bright_red': '\033[91;1m',
    'bright_green': '\033[92;1m'
}
W = '\033[0m'

class Server(webui, CommandAnalyze.CommandAnalysiser):
    def __init__(self, 
                 token: str, 
                 secret: str,
                 url: str = None,
                 port: int = 8000,):
        super().__init__()
        super(CommandAnalyze.CommandAnalysiser, self).__init__()
        self.token = token
        self.secret = secret

        self.line_bot_api = LineBotApi(token)
        self.handler = WebhookHandler(secret)

        self.port = port

        if url is not None:
            self.ngrok_url = url
            _print(f"ngrok URL: {C['cyan']}{self.ngrok_url}{W}")
            self.update_line_webhook_url(self.ngrok_url)
        else:
            self.set_ngrok()
        
        self.app = FastAPI()
        self.router = APIRouter()

        self.app.mount("/images", StaticFiles(directory="./static", html=True), name="images")
        self.app = gr.mount_gradio_app(self.app, self.gr_interface, path="/gradio")
        self.set_routes()
        
    def set_ngrok(self,):
        t = threading.Thread(target=self.start_ngork)
        t.start()

        self.ngrok_url = self.get_ngrok_url()

        if self.ngrok_url is not None:
            _print(f"ngrok URL: {C['cyan']}{self.ngrok_url}{W}")
            self.update_line_webhook_url(self.ngrok_url)
        else:
            _print(f"{C['red']}Failed to get ngrok URL{W}")
            os._exit(1)

    def start_ngork(self):
        try:
            subprocess.run(['src/ngrok.exe', 'http', str(self.port)], stdout=subprocess.PIPE).stdout.decode('utf-8')
            _print(f"{C['bright_green']}Ngrok started{W}")
        except FileNotFoundError as e:
            _print(f"{C['red']}File not found error: {e}")
            _print(f"{C['red']}Please download ngrok and place it in the src folder{W}") 
            os._exit(1)
        except subprocess.CalledProcessError as e:
            _print(f"{C['red']}Subprocess error: {e}")
            os._exit(1)

    def get_ngrok_url(self,):
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            data = response.json()
            public_url = data['tunnels'][0]['public_url']
            return public_url
        except Exception as e:
            _print(f"{C['red']}Error getting ngrok URL: {e}{W}")
            _print(f"{C['yellow']}Starting ngrok...{W}")
            return None
        
    def send_message(self, message):
        self.line_bot_api.broadcast(TextSendMessage(text=message))

    def reply_message(self, reply_token, message):
        self.line_bot_api.reply_message(reply_token, TextSendMessage(text=message))

    def reply_image(self, reply_token, image_path):
        self.line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=image_path, preview_image_url=image_path))

    def send_image(self, image_path):
        self.line_bot_api.broadcast(ImageSendMessage(original_content_url=image_path, preview_image_url=image_path))

    def set_routes(self):
        @self.app.post("/callback")
        async def callback(request: Request):
            signature = request.headers.get('X-Line-Signature')
            
            body = await request.body()
            body = body.decode('utf-8')

            try:
                self.handler.handle(body, signature)
            except InvalidSignatureError:
                raise HTTPException(status_code=400, detail="Invalid signature")

            return JSONResponse(content={"status": "OK"})

        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_text_message(event):
            _print(f"Received text message: {event.message.text}")
            response = self.run_analyze(event.message.text, event.source.user_id)
            if response[0] == 'msg':
                self.reply_message(event.reply_token, response[1])
            else:
                self.reply_image(event.reply_token, response[1])


        @self.handler.add(MessageEvent, message=ImageMessage)
        def handle_image_message(event):
            import tempfile
            message_content = self.line_bot_api.get_message_content(event.message.id)
            
            with tempfile.NamedTemporaryFile(dir="./static", delete=False, suffix='.jpg') as tf:
                for chunk in message_content.iter_content():
                    tf.write(chunk)
                tempfile_path = tf.name

            image_url = f'{self.ngrok_url}/images/{os.path.basename(tempfile_path)}'
            
            self.reply_image(event.reply_token, image_url)

        @self.app.get("/",)
        async def root():
            # 將 Gradio 應用嵌入到 FastAPI 的 HTML 中
            return 'Gradio app is running at /gradio', 200
        

    def update_line_webhook_url(self, new_url):
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            data = {
                "endpoint": f"{new_url}/callback"
            }
            response = requests.put(
                "https://api.line.me/v2/bot/channel/webhook/endpoint",
                headers=headers,
                json=data
            )
            if response.status_code == 200:
                _print(f"{C['green']}LINE Webhook URL updated successfully{W}")
            else:
                _print(f"{C['red']}Failed to update LINE Webhook URL: {response.status_code}, {response.text}{W}")
        except Exception as e:
            _print(f"{C['red']}Error updating LINE Webhook URL: {e}{W}")

    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)

def _print(msg):
    print(f"{W}[DeBug] [Server] | {msg}{W}")



if __name__ == "__main__":
    server = Server(token="D8I69TjO5K8ne0oFnRn2CA6d3iIP8qd+rL2jtSuWPBgmPLbn9ZsAwVrGkYts6SeVigU3MtzTbzvm0RihxGJdXVOoko72ZmcOgoX96IVbdpJpIHySWeJj7GUH+fY7JVeN5N49Ow1oIjHDPcD8we5f3QdB04t89/1O/w1cDnyilFU=",
                    secret="c36cb258c48e9a3a747acd946dd72b21",)
    server.run()
