from transformers import BertForSequenceClassification, BertTokenizer
import torch

class Sentiment:
    def __init__(self, model_path: str = './src/models'):

        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = BertTokenizer.from_pretrained(model_path)


    def predict_sentiment(self, text: str):
        if text.isdigit() or all(c in '０１２３４５６７８９' for c in text):
            return 'msg', "輸入僅包含數字或全形數字，無法進行判斷。"

  
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

       
        outputs = self.model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()


        sentiment_map = {0: "負面", 2: "正面"}
        sentiment = sentiment_map.get(prediction, "未知")
        return 'msg', f"模型預測的感情為：{sentiment}"
