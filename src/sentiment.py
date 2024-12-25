from src.color import C, W
import joblib

class Sentiment():
    def __init__(self,
                 model_path: str = './src/models/sentiment_model.pkl',
                 vectorizer_path: str = './src/models/vectorizer.pkl',
                 stopwords_path: str = './src/models/stopwords.txt'):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)

        self.stop_words = set()

        with open(stopwords_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.stop_words.add(line.strip())

    def predict_sentiment(self, text):
        if text.isdigit() or all(c in '０１２３４５６７８９' for c in text):
            return 'msg', "輸入僅包含數字或全形數字，無法進行判斷。"
        
        text_vectorized = self.vectorizer.transform([text])
        prediction = self.model.predict(text_vectorized)
        sentiment_map = {0: '負面', 2: '正面'}
        sentiment = sentiment_map.get(prediction[0], '未知')
        return 'msg', f"模型預測的感情為：{sentiment}"