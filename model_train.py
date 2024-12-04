import os
import pandas as pd
import numpy as np
import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# 獲取當前文件的目錄
current_dir = os.path.dirname(os.path.abspath(__file__))

# 加載停用詞表
stopwords = set()
stopwords_path = os.path.join(current_dir, 'stopwords.txt')
with open(stopwords_path, 'r', encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.strip())

# 初始化陣列
data = []

# 文件路徑
file_path = os.path.join(current_dir, 'data.txt')

# 打開開關讀取數據文件
with open(file_path, 'r', encoding='utf-8') as f:
    # 跳過標題行
    next(f)
    for line_num, line in enumerate(f, 2):
        # 去除行首行尾的空白字符
        line = line.strip()
        if line:
            # 使用 rsplit 分割行
            line_parts = line.rsplit(',', 1)
            if len(line_parts) == 2:
                text, label = line_parts
                label = label.strip()
                if label in {'0', '1', '2'}:
                    # 去除可能的引號和空白字符
                    text = text.strip('"').strip()
                    data.append({'text': text, 'label': int(label)})
                else:
                    print(f"第 {line_num} 行標籤不正确，跳過該行：{line}")
            else:
                print(f"第 {line_num} 行格式不正确，跳過該行：{line}")

# 將列表轉換為 DataFrame
df = pd.DataFrame(data)

# 顯示前幾列數據
print(df.head().to_string(index=False))

# 檢查 DataFrame 列名
print("DataFrame 列名：", df.columns.tolist())

# 檢查數據中各類別的樣本數量
print("數據中各類別的樣本數量：")
print(df['label'].value_counts())

# 文本清理函數
def clean_text(text):
    # 去除英文字符和數字
    text = re.sub(r'[A-Za-z0-9]', '', text)
    # 去除特殊字符（保留中文字符、韓文和常見標點符號）
    # Unicode 中文\u4e00-\u9fa5, 日文\u3040-\u30FF（可以考慮增加）, 韓文\uAC00-\uD7AF
    text = re.sub(r'[^\u4e00-\u9fa5\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F。，“”！？～；：!\.]', '', text) 
    # 去除多餘的空格
    text = text.strip()
    return text

df['cleaned_text'] = df['text'].apply(clean_text)

# 分詞
def tokenize(text):
    tokens = jieba.lcut(text)
    return ' '.join(tokens)

df['tokenized_text'] = df['cleaned_text'].apply(tokenize)

# 去除停用词
def remove_stopwords(text):
    words = text.split()
    words = [word for word in words if word not in stopwords]
    return ' '.join(words)

df['final_text'] = df['tokenized_text'].apply(remove_stopwords)

# 檢查 DataFrame 是否包含 'final_text' 列
print("DataFrame 列名：", df.columns.tolist())

# 3. 特徵提取
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['final_text'])
y = df['label']

# 4. 劃分訓練集和測試集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# 5. 模型訓練
model = MultinomialNB()
model.fit(X_train, y_train)

# 6. 模型評估
y_pred = model.predict(X_test)
print('分類報告：')
print(classification_report(y_test, y_pred, labels=[0, 1, 2], digits=4))
print('混淆矩陣：')
print(confusion_matrix(y_test, y_pred, labels=[0, 1, 2]))

# 7. 保存模型和向量化器
joblib.dump(model, os.path.join(current_dir, 'sentiment_model.pkl'))
joblib.dump(vectorizer, os.path.join(current_dir, 'vectorizer.pkl'))

# debug = True
# print(debug)