import gradio as gr
from src.color import C, W

class webui(object):
    def __init__(self):
        with gr.Blocks() as self.gr_interface:
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 設定區")
                    self.config1 = gr.Number(label="設定1", value=10)
                    self.config2 = gr.Textbox(label="設定2", placeholder="輸入文字")
                    self.toggle = gr.Checkbox(label="啟用功能",elem_id="switch")

                    with gr.Row():
                        self.save_apply_btn = gr.Button("儲存並套用")
                        self.load_cfg_btn = gr.Button("Load Config")
                        self.save_cfg_btn = gr.Button("儲存")

                with gr.Column():
                    gr.Markdown("### 顯示user數量區")
                    self.user_count_display = gr.Textbox(label="目前user數量", value="50", interactive=False)

            with gr.Row():
                # gr.Markdown("### 日誌輸出")
                self.log_output = gr.Textbox(label="日誌輸出", placeholder="顯示日誌內容", lines=10, interactive=False)

            # Define actions for buttons
            self.save_apply_btn.click(self.save_and_apply_config, [self.config1, self.config2, self.toggle], self.log_output)
            self.load_cfg_btn.click(self.load_config, outputs=self.log_output)
            self.save_cfg_btn.click(self.save_config, outputs=self.log_output)

    def greet(self, input_text):
        return f"Hello, {input_text}!"

    def save_and_apply_config(self, config1, config2, toggle):
        return f"Configuration applied: 設定1={config1}, 設定2={config2}, 啟用功能={toggle}"

    def load_config(self):
        return "Loaded configuration: default"

    def save_config(self):
        return "Configuration saved!"

    def start_debugui(self):
        self.gr_interface.launch(server_port=4521)
