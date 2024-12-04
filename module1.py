import os
import pandas as pd
import numpy as np
import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# 獲取當前文件的目錄
current_dir = os.path.dirname(os.path.abspath(__file__))

# 使用絕對路徑載入模型和向量化器
model_path = os.path.join(current_dir, 'sentiment_model.pkl')
vectorizer_path = os.path.join(current_dir, 'vectorizer.pkl')

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# 加载停用词表
stopwords = set()
stopwords_path = os.path.join(current_dir, 'stopwords.txt')
with open(stopwords_path, 'r', encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.strip())

def predict_sentiment(text):
    text_vectorized = vectorizer.transform([text])
    prediction = model.predict(text_vectorized)
    sentiment_map = {0: '負面', 1: '中性', 2: '正面'}
    sentiment = sentiment_map.get(prediction[0], '未知')
    return sentiment

def handle_message(input_text):
    sentiment = predict_sentiment(input_text)
    return f"模型預測的感情為：{sentiment}"
