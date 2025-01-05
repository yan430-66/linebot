import requests
from datetime import datetime, timedelta
import yaml

class catch_news:
    def __init__(self,
                 api_key: str,
                 base_url: str,):
            self.api_key = api_key
            self.base_url = base_url
    
    def fetch_google_news(self, query: str, language:str, from_date: str, to_date: str):
        url = f'{self.base_url}/everything?q={query}&language={language}&apiKey={self.api_key}'
        
        if from_date:
            url += f'&from={from_date}'
           
        if to_date:
            url += f'&to={to_date}'
              

        response = requests.get(url)

        if response.status_code == 200:
            return 'msg', response.json()
        else:
            print(f"Failed to fetch news: {response.status_code}")  
            return 'err', None
    
    def parse_date_input(self, date_input: str):
        try:
            date_obj = datetime.strptime(date_input, '%Y-%m-%d')
            return 'msg', f"成功解析日期 {date_obj.strftime('%Y-%m-%d')}"
        except ValueError:
                return 'err', "日期格式錯誤，請重新輸入。"

    def get_valid_date(self, prompt: str):

        while True:
            date_input = input(prompt)
            result_type, message = self.parse_date_input(date_input)
            if result_type == 'err':
                print(message)
                continue
            
            date_obj = datetime.strptime(date_input, '%Y-%m-%d')
            one_month_ago = datetime.today() - timedelta(days=31)
            if date_obj > datetime.today():
                print("請輸入31天內的日期。")
            elif date_obj < one_month_ago:
                print("日期範圍不可超過31天前。")
            else:
                return date_input


    def display_news(self, query: str, language: str, from_date_input: str, to_date_input: str):
        # 解析日期
        from_date_msg, from_date = self.parse_date_input(from_date_input)
        if from_date is None:
            return 'err', from_date_msg

        to_date_msg, to_date = self.parse_date_input(to_date_input)
        if to_date is None:
            return 'err', to_date_msg

        # 取得新聞數據
        fetch_status, news_data = self.fetch_google_news(query, language, from_date, to_date)
        if fetch_status == 'err' or news_data is None:
            return 'err', "無法取得新聞數據。"

        # 格式化新聞數據，限制數量
        max_articles = 10  # 設定返回的最大新聞數量
        messages = []
        for i, article in enumerate(news_data.get('articles', [])):
            if i >= max_articles:  # 超過最大數量時停止
                break
            if query.lower() in article.get('title', '').lower() or query.lower() in (article.get('description') or '').lower():
                message = (
                    f"Title: {article.get('title', '無標題')}\n"
                    f"Description: {article.get('description', '無描述')}\n"
                    f"URL: {article.get('url', '無連結')}\n"
                    "--------------------------------------------"
                )
                messages.append(message)

        if not messages:
            return 'msg', "沒有相關新聞。"

        # 拼接消息
        final_message = "\n".join(messages)
        return 'msg', final_message


