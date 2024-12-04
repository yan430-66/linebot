import gradio as gr

class webui():
    def __init__(self):
                self.gr_interface = gr.Interface(
            fn=self.greet,
            inputs=gr.components.Textbox(label='Input'),
            outputs=gr.components.Textbox(label='Output'),
            allow_flagging='never'
        )

        

    def greet(self, text: str) -> str:
        return text