import gradio as gr
import sys
import os
import yaml
import threading
import subprocess
from gradio_log import Log
from src.color import C, W
from logs.log import Logger, WEB_LOG, SERVER_LOG, log_pth

###########################################
##  新增cfg選項要按照格式                   
##  頁面顯示要記得改 line 29 以下的部分     
##  self.save_cfg_btn.click input 要改     
##  self.load_cfg_btn.click output 要改    
###########################################

class webui(object):
    def __init__(self):
        SERVER_LOG = log_pth()
        sys.stdout = Logger(WEB_LOG)
        self.server_state = "Stop"  
        self.server_thread = None
        self.file_path = "./cfg.yaml"
        self.create_config()
        
        with gr.Blocks(css="#server-log-comp-id {min-height: 200px; max-height: 800px}") as self.gr_interface:
            self.config = self.load_config()
            self.reload_html = gr.HTML()
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 設定區")
                    self.token = gr.Textbox(label="LINE CHANNEL ACCESS TOKEN", placeholder="LINE CHANNEL ACCESS TOKEN", value=self.config["token"], interactive=True)
                    self.secret = gr.Textbox(label="LINE CHANNEL SECRET", placeholder="LINE CHANNEL SECRET", value=self.config["secret"], interactive=True)
                    self.azure_endpoint = gr.Textbox(label="Azure Endpoint", placeholder="Azure Endpoint", value=self.config["azure_endpoint"], interactive=True)
                    self.azure_key = gr.Textbox(label="Azure API KEY", placeholder="Azure API", value=self.config["azure_key"], interactive=True)
                    self.url = gr.Textbox(label="ngrok URL", placeholder="URL", value=self.config["url"], interactive=True)
                    self.port = gr.Number(label="Port:", value=self.config["port"], interactive=True)
                    
                    # self.toggle = gr.Checkbox(label="啟用功能", elem_id="switch")
    
                    with gr.Row():
                        self.load_cfg_btn = gr.Button("Load Config")
                        self.save_cfg_btn = gr.Button("儲存")
                        self.ref_btn = gr.Button('重新整理')

                with gr.Column():
                    gr.Markdown("### Server狀態: ")
                    self.server_log = Log(SERVER_LOG, dark=True, xterm_font_size=18, every=0.3, elem_id="server-log-comp-id", height=300)              
    
            with gr.Column():
                with gr.Row():
                    self.start_btn = gr.Button("Start", elem_id="start-btn", every=60.0)
                    self.stop_btn = gr.Button("Stop", elem_id="stop-btn")
                    self.restart_btn = gr.Button("Restart", elem_id="restart-btn")
                gr.Markdown("### 日誌輸出")
                self.web_log = Log(WEB_LOG, dark=True, xterm_font_size=18, every=0.3, elem_id="web-log-comp-id", height=400)          
                
            self.ref_btn.click(
                fn=lambda: None,
                js='window.location.reload()' 
            )

            self.load_cfg_btn.click(
                self.update_config, 
                outputs=[self.token, self.secret, self.port, self.url, self.azure_endpoint, self.azure_key],
            )

            self.save_cfg_btn.click(
                self.save_config,
                inputs=[self.token, self.secret, self.port, self.url, self.azure_endpoint, self.azure_key], 
                outputs=self.web_log,  
            )

            self.start_btn.click(
                self.start_server, 
                outputs=self.web_log  
            )

            self.stop_btn.click(
                self.stop_server,
                outputs=[self.web_log, self.server_log, self.reload_html],
            )

            self.restart_btn.click(
                self.restart_server,
                outputs=[self.web_log,],
            )

            _print(f"WebUI initialized")
    
    def save_and_apply_config(self, config1, config2, toggle):
        msg = f"Configuration applied: 設定1={C['bright_green']}{config1}{W}, 設定2={C['bright_green']}{config2}{W}, 啟用功能={C['blue']}{toggle}{W}"
        _print(msg)
        return '' 
    
    def create_config(self):
        if not os.path.exists(self.file_path):
            default_config = {"token": f"LINE CHANNEL ACCESS TOKEN", 
                            "secret": f"LINE CHANNEL SECRET",
                            "azure_endpoint" : "azure endpoint",
                            "azure_key" : "AZURE API KEY",
                            "port": 8000,
                            "url" : None}
            with open(self.file_path, "w", encoding="utf-8") as yaml_file:
                yaml.dump(default_config, yaml_file, default_flow_style=False, allow_unicode=True)
            _print(state=C['suc'], msg=f"Configuration created!")
            _print("You should edit the configuration file before starting the server.", C['warn'])
    
    def load_config(self):
        with open(self.file_path, "r", encoding="utf-8") as yaml_file:
            loaded_config = yaml.safe_load(yaml_file)
        _print("Loaded configuration")
        if loaded_config["token"] == "LINE CHANNEL ACCESS TOKEN" or loaded_config["secret"] == "LINE CHANNEL SECRET":
            _print("You should edit the configuration file before starting the server.", C['warn'])
        return loaded_config
    
    def update_config(self):
        self.config = self.load_config()
        return self.config["token"], self.config["secret"], self.config["port"], self.config["url"], self.config["azure_endpoint"], self.config["azure_key"]
    
    def save_config(self, token, secret, port, url, azure_endpoint, azure_key):
        self.config["token"] = token
        self.config["secret"] = secret
        self.config["port"] = port
        self.config["url"] = url
        self.config["azure_endpoint"] = azure_endpoint
        self.config["azure_key"] = azure_key
        _print(f"Configuration updated: {secret}", C['inf'])
        with open(self.file_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(self.config, yaml_file, default_flow_style=False, allow_unicode=True)
        _print(state=C['suc'], msg="Configuration saved!")
        return "\n"
    
    def start_server(self):
        if self.server_state == "Stop":
            _print(f'Server start', C['inf'])
            self.server_thread = threading.Thread(target=self.start_line_server, daemon=True,)
            self.server_thread.start()
            self.server_state = "Running"
            return ""
        else:
            _print(f'Server already running', C['warn'])
            return ""
        
    def start_line_server(self):
        python_path = sys.executable
        self.server_process = subprocess.Popen([
            python_path, './server.py', 
            '-cfg', self.file_path, 
            '-L', SERVER_LOG
        ])
        self.server_process.wait()
        print(f'{C["warn"]} [WebUi] | Server Stoped')
        self.server_state = "Stop"

    def stop_server(self):
        res, html = self.refresh_log()

        if self.server_state == "Running" :
            self.server_process.terminate()
            self.server_state = "Stop"
            _print(f'Server stopped', C['inf'])
            self.server_log.log_file = log_pth()
            self.server_process = None

            return f"{W}{C['inf']} [WebUi] | Server stopped{W}\n", res, html
        else:
            _print(f'Server not running', C['warn']) 
            self.server_log.log_file = log_pth() 
            return f"{W}{C['warn']} [WebUi] | Server not running{W}\n", res, html
        
    def restart_server(self):
        try:
            if self.server_state == "Running":
                self.stop_server()
                self.start_server()
            else:
                self.start_server()
            return f'{W}{C["suc"]} [WebUi] | Server restarted{W}'
        except Exception as e:
            _print(f"Error restarting server: {e}", C['err'])
            return ''

    def refresh_log(self):
        try:
            reload_script = "<script>setTimeout(function(){window.location.reload();}, 100);</script>"
            reload_script = "<script>window.location.reload();</script>"
            _print("Server log refreshed.", C['inf'])
            res = f"{W}{C['inf']} [WebUi] | Server log refreshed{W}\n"
            return res, reload_script
        except Exception as e:
            _print(f"Error refreshing log: {e}", C['err'])
            res = f"{W}{C['err']} [WebUi] | Error refreshing log: {e}{W}\n"
            return res, ""
    
    def start_debugui(self):
        self.gr_interface.launch(server_port=4521,)
    
def _print(msg: str = '', state: str = '[INFO]'):
    print(f"{W}{state} [WebUi] | {msg}{W}")
    return 

if __name__ == "__main__":
    ui = webui()
    ui.start_debugui()
