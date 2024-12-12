import os
import uvicorn
import requests
import subprocess
import threading
import uvicorn.config
import argparse
import uvicorn.server
import sys
from src.color import C, W
from logs.log import Logger
from src import CommandAnalyze
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

class Server(CommandAnalyze.CommandAnalysiser):
    def __init__(self, 
                 token: str, 
                 secret: str,
                 url: str = None,
                 port: int = 8000,
                 server_log: str = None):
        super().__init__()
        super(CommandAnalyze.CommandAnalysiser, self).__init__()
        self.token = token
        self.secret = secret

        self.line_bot_api = LineBotApi(token)
        self.handler = WebhookHandler(secret)

        self.port = port
        url = self.get_ngrok_url()
        if url is not None:
            self.ngrok_url = url
            _print(f"ngrok URL: {C['cyan']}{self.ngrok_url}{W}")
            self.update_line_webhook_url(self.ngrok_url)
        else:
            self.set_ngrok()
        
        self.app = FastAPI()
        self.router = APIRouter()

        self.app.mount("/images", StaticFiles(directory="./static", html=True), name="images")
        # self.app = gr.mount_gradio_app(self.app, self.gr_interface, path="/gradio")
        self.set_routes()
        _print(f"Server initialized", C['suc'])
        
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
            _print(f"{C['red']}Error getting ngrok URL: {e}{W}", state=C['err'])
            _print(f"{C['yellow']}Starting ngrok...{W}")
            return None

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
                _print(f"Replying with message: {response[1]}")
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
                _print(f"{C['green']}LINE Webhook URL updated successfully{W}",state=C['suc'])
            else:
                _print(f"{C['dark_red']}Failed to update LINE Webhook URL: {response.status_code}, {response.text}{W}", state=C['err'])
                _print(f"{C['yellow']}Please check your LINE Channel Access Token and Secret{W}", state=C['warn'])
                _print(f"{C['yellow']}Exiting...{W}")
                sys.exit(-1)
        except Exception as e:
            _print(f"{C['yellow']}Exiting...{W}")
            _print(f"{C['red']}Error updating LINE Webhook URL: {e}{W}",state=C['err'])
            sys.exit(-1)

    def send_message(self, message):
        self.line_bot_api.broadcast(TextSendMessage(text=message))

    def reply_message(self, reply_token, message):
        self.line_bot_api.reply_message(reply_token, TextSendMessage(text=message))

    def reply_image(self, reply_token, image_path):
        self.line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=image_path, preview_image_url=image_path))

    def send_image(self, image_path):
        self.line_bot_api.broadcast(ImageSendMessage(original_content_url=image_path, preview_image_url=image_path))

    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="info")

def _print(msg: str = '',
           state: str = C['inf'],):
    print(f"{W}{state} [Server] | {msg}{W}")


if __name__ == "__main__":
    
    # server = Server(token="D8I69TjO5K8ne0oFnRn2CA6d3iIP8qd+rL2jtSuWPBgmPLbn9ZsAwVrGkYts6SeVigU3MtzTbzvm0RihxGJdXVOoko72ZmcOgoX96IVbdpJpIHySWeJj7GUH+fY7JVeN5N49Ow1oIjHDPcD8we5f3QdB04t89/1O/w1cDnyilFU=",
    #                 secret="c36cb258c48e9a3a747acd946dd72b21",)
    # server.run()
    parser = argparse.ArgumentParser()
    parser.add_argument('-T', type=str, help='LINE CHANNEL ACCESS TOKEN',)
    parser.add_argument('-S', type=str, help='LINE CHANNEL SECRET', )
    parser.add_argument('-P', type=int, help='PORT', default=8000)
    parser.add_argument('-L', type=str, help='log file', default=None)
    parser.add_argument('-ngrok', type=str, help='ngrok url if opened', default=None)
    args = parser.parse_args()
    sys.stdout = Logger(args.L)
    _print(' ')
    _print('Server initializing...', C['inf'])
    server = Server(token=args.T, secret=args.S, port=args.P, url=args.ngrok, server_log=args.L)
    server.run()
