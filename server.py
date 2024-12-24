import os
import uvicorn
import requests
import subprocess
import uvicorn.config
import argparse
import uvicorn.server
import sys
import yaml
from src.color import C, W
from logs.log import Logger, log_pth
from src.CommandAnalyze import CommandAnalysiser
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

class Server(CommandAnalysiser):
    def __init__(self, 
                 config_path: str = './cfg.yaml',
                 server_log: str | bool = None):
        self.load_cfg(config_path)
        if server_log and type(server_log) != str:
            pth = log_pth()
            _print(f"Server log {C['dark_blue']}:{pth}{W}, will save log", C['inf'])
            sys.stdout = Logger(pth)
        elif server_log and type(server_log) == str:
            _print(f"Server log {C['dark_blue']}:{server_log}{W}, will save log", C['inf'])
            sys.stdout = Logger(server_log)
        elif server_log is None:
            _print(f"log option is {C['dark_blue']}None{W}, will not save log", C['inf'])

        super(CommandAnalysiser, self).__init__(weather_api_key=self.args.weather_api, 
                                                crypto_base_url=self.args.CoinMarketCapAPI_BASE_URL, 
                                                crypto_api_key=self.args.CoinMarketCapAPI_KEY,
                                                cc_api_key=self.args.ExchangeRatesAPI_KEY,
                                                cc_base_url=self.args.ExchangeRatesAPI_BASE_URL)
        
        self.token = self.args.token
        self.secret = self.args.secret

        self.line_bot_api = LineBotApi(self.token)
        self.handler = WebhookHandler(self.secret)

        self.port = self.args.port
        if self.args.url is None:
            url = self.get_ngrok_url()
            if url is not None:
                self.ngrok_url = url
                _print(f"ngrok URL: {C['cyan']}{self.ngrok_url}{W}")
                self.update_line_webhook_url(self.ngrok_url)
            else:
                self.set_ngrok()
        else:
            self.set_ngrok()
        
        self.app = FastAPI()
        self.router = APIRouter()

        self.app.mount("/images", StaticFiles(directory="./static", html=True), name="images")
        # self.app = gr.mount_gradio_app(self.app, self.gr_interface, path="/gradio")
        self.set_routes()
        _print(f"Server initialized", C['suc'])
        
    def set_ngrok(self,):
        self.start_ngork()
        
        self.ngrok_url = self.get_ngrok_url()

        if self.ngrok_url is not None:
            _print(f"ngrok URL: {C['cyan']}{self.ngrok_url}{W}")
            self.update_line_webhook_url(self.ngrok_url)
        else:
            _print(f"{C['red']}Failed to get ngrok URL{W}")
            os._exit(1)

    def start_ngork(self):
        _print(f"{C['yellow']}Starting ngrok...{W}")
        try:
            self.ngrok_process = subprocess.Popen(['src/ngrok.exe', 'http', str(self.port)], stdout=subprocess.PIPE)
            # subprocess.run(['src/ngrok.exe', 'http', str(self.port)], stdout=subprocess.PIPE).stdout.decode('utf-8')
            print(f"{W}{C['suc']} [Server] | Ngrok started{W}")
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
            return None
        
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
                if self.ngrok_process is not None:
                    self.ngrok_process.terminate()
                sys.exit()
        except Exception as e:
            if self.ngrok_process is not None:
                    self.ngrok_process.terminate()
            _print(f"{C['red']}Error updating LINE Webhook URL: {e}{W}",state=C['err'])
            _print(f"{C['yellow']}Exiting...{W}")
            sys.exit()

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
            elif response[0] == 'img':
                self.reply_image(event.reply_token, response[1])
            elif response[0] in ['err', 'warn']:
                _print(f"{response[1]}", state=C[response[0]])
            else:
                _print(f"Unknown response type: {response[0]}", state=C['err'])
                _print(f"Response: {response[1]}", state=C['err'])

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

    def send_message(self, message):
        self.line_bot_api.broadcast(TextSendMessage(text=message))

    def reply_message(self, reply_token, message):
        self.line_bot_api.reply_message(reply_token, TextSendMessage(text=message))

    def reply_image(self, reply_token, image_path):
        self.line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=image_path, preview_image_url=image_path))

    def send_image(self, image_path):
        self.line_bot_api.broadcast(ImageSendMessage(original_content_url=image_path, preview_image_url=image_path))

    def load_cfg(self, config_path):
        config = yaml.load(open(config_path, 'r', encoding='UTF-8'), Loader=yaml.FullLoader)
        self.args = argparse.Namespace(**config)
        print('[Debug] [main] | cfg loaded.')

    def run(self):
        uvicorn.run(self.app, host="127.0.0.1", port=self.port, log_level="info")

def _print(msg: str = '',
           state: str = C['inf'],):
    print(f"{W}{state} [Server] | {msg}{W}")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-cfg', type=str, help='cfg path ', default='./cfg.yaml')
    parser.add_argument('-L', type=str, help='log file', default=None)
    args = parser.parse_args()
    if args.L is not None and type(args.L) == str:
        _print(f'{C["dark_blue"]}{args.L}{W}', C['inf'])
        sys.stdout = Logger(args.L)
    print(' ')
    _print('Server initializing...', C['inf'])
    server = Server(config_path=args.cfg, server_log=args.L)
    server.run()
