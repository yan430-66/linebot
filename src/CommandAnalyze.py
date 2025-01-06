from .color import C, W
from .sentiment import Sentiment
from .weather_api import Weather_clm
from .coin import CryptoPrice
from .currency import CurrencyConverter
from .stock import Stock
from .news import catch_news
from .youbike import YouBike
class Command():
    def __init__(self, ):
        
        self.user_state = {}
        self.cmd_dic = {
            '/test': [self.test, "discrisption of test"],
            '/test2': [self.test2, "discrisption of test2"],
            '/test3': [self.test3, "discrisption of test3"],
            '/help': [self.help, "discrisption of help"],
            '/?': [self.help, "discrisption of help"],
            '/nserch': [self.nserch, "serch nhentai.net by code"],
            '/ns': [self.nserch, "serch nhentai.net by code"],
            '1': [self.chosise_1, "sentiment command"],
            '/W': [self._weather, "get weather by region and area"],
            '2': [self.chosise_2, "get coin price by coin symbol"],
            '3': [self.chosise_3, "currency converter"],
            '4': [self.chosise_4, "stock price by symbol"],
            '5': [self.chosise_5, "news :D"],
            '6': [self.chosise_6, "Youbike station"],
                   }
        
        self.cmd_list = list(self.cmd_dic.keys())

    def _weather(self, ):
        self.user_state[self.user_id] = self._get_weather
        res = 'msg', f'請輸入地區名稱'
        return res

    def _get_weather(self,
                     region: str,
                     area: str = None):
        return self.weather.get_weather(region, area=area)
    
    def _get_converter(self,
                       amount: str, 
                       from_currency: str,
                       a: str, 
                       to_currency: str,
                    ):

        return self.cc.convert_currency(from_currency=from_currency, to_currency=to_currency, a=a, amount=float(amount))
                  
   

    def chosise_1(self,):
        self.user_state[self.user_id] = self.sentiment
        return 'msg', f'請傳送一則訊息讓 module1 判斷。'
    
    def chosise_2(self,):
        self.user_state[self.user_id] = self.coin
        return 'msg', f'輸入要查詢之加密貨幣(e.g., BTC, ETH): '

    def chosise_3(self,):
        self.user_state[self.user_id] = self._get_converter # = {user_id: self._converter}
        res = 'msg', f'Enter the amount and currency conversion (e.g., 100 USD to EUR): '
        return res
        
    def chosise_4(self,):
        self.user_state[self.user_id] = self.get_stock_code
        return 'msg', f'輸入股票代碼 (如 AAPL, MSFT): ' 
    
    def chosise_5(self,):
        self.user_state[self.user_id] = self.get_query
        return 'msg', f"請輸入要查詢的關鍵字:"
    def chosise_6(self):
        self.user_state[self.user_id] = self.get_youbike_region
        return 'msg', '請輸入地區名稱(e.g.,台北):'

    def get_youbike_region(self, region: str):
        self.user_state[f"{self.user_id}_region"] = region.strip()
        self.user_state[self.user_id] = self.get_youbike_area
        return 'msg', '請輸入查詢區域(e.g.,信義區):'

    def get_youbike_area(self, area: str):
        region = self.user_state[f"{self.user_id}_region"]
        self.user_state[f"{self.user_id}_area"] = area.strip()
        res_type, res_message = self.yb.display_stations_by_area(city_name=region, area=area.strip())
        if res_type == 'err':
            return 'err', res_message

        self.user_state[self.user_id] = self.get_youbike_station
        return 'msg', f"{res_message}\n\n請輸入查詢之站點:"

    def get_youbike_station(self, station: str):
        region = self.user_state.pop(f"{self.user_id}_region")
        area = self.user_state.pop(f"{self.user_id}_area")
        return self.yb.display_station_info(city_name=region, area=area, station=station.strip())

    def get_query(self, query: str):
        self.user_state[f"{self.user_id}_query"] = query.strip()
        self.user_state[self.user_id] = self.get_language
        return 'msg', f"請輸入搜尋語言 (預設 zh): " or 'zh'
    
    def get_language(self, language: str):
        self.user_state[f"{self.user_id}_language"] = language.strip()
        self.user_state[self.user_id] = self.get_from_date
        return 'msg', f"請輸入要搜尋的起始日期（格式: YYYY-MM-DD）"
    
    def get_from_date(self, from_date: str):
        self.user_state[f"{self.user_id}_from_date"] = from_date.strip()
        self.user_state[self.user_id] = self.get_to_date
        return 'msg' , f"請輸入要搜尋的結束日期（格式: YYYY-MM-DD）"

    def get_to_date(self, to_date:str):
        query = self.user_state.pop(f"{self.user_id}_query")
        language = self.user_state.pop(f"{self.user_id}_language")
        from_date = self.user_state.pop(f"{self.user_id}_from_date")
        return self.ct.display_news(query = query, language = language , from_date_input = from_date, to_date_input = to_date.strip())

    def coin(self, msg: str):
        return self.co.display_price(msg)
    
    def sentiment(self, msg: str):
        return self.se.predict_sentiment(msg)

    def get_stock_code(self, stock_code: str):
        self.user_state[f"{self.user_id}_stock_code"] = stock_code.strip()
        self.user_state[self.user_id] = self.get_start_date
        return 'msg', f'請輸入開始日期 (格式: YYYY-MM-DD):'

    def get_start_date(self, start_date: str):
        self.user_state[f"{self.user_id}_start_date"] = start_date.strip()
        self.user_state[self.user_id] = self.get_end_date
        return 'msg', f'請輸入結束日期 (格式: YYYY-MM-DD):'

    def get_end_date(self, end_date: str):
        stock_code = self.user_state.pop(f"{self.user_id}_stock_code")
        start_date = self.user_state.pop(f"{self.user_id}_start_date")
        return self.st.display_stock_info(stock_code=stock_code, start_date_input=start_date, end_date_input=end_date.strip())

    def nserch(self, text: str, *args):
        return 'msg', f'https://nhentai.net/g/{text}/'

    def test(self, *args):
        return 'msg', f'test command run successfully and get {args}'
    
    def test2(self, ):
        return 'msg', f'test2 command run successfully'
    
    def test3(self, a1, a2):
        return 'msg', f'test2 command run successfully{a1} and {a2}'
    
    def help(self, ):
        res = ''
        for k, v in self.cmd_dic.items():
            res += f'Command description{k} | {v[1]}\n'
            res += '\n'
        return 'msg', res

class CommandAnalysiser(Command):
    def __init__(self, 
                 test_class: int,
                 weather_api_key: str,
                 crypto_api_key: str,
                 crypto_base_url: str,
                 cc_api_key: str,
                 cc_base_url: str,
                 news_api_key:str,
                 news_base_url:str
                 ):
        self.test_class = test_class
        self.weather = Weather_clm(weather_api_key)
        self.cc = CurrencyConverter(api_key=cc_api_key, base_url=cc_base_url)
        self.co =  CryptoPrice(api_key=crypto_api_key, base_url=crypto_base_url)
        self.se = Sentiment()
        self.st = Stock()
        self.ct = catch_news(api_key=news_api_key, base_url= news_base_url)
        self.yb = YouBike()
        super().__init__()

    def analyze(self, cmd_text: str): 
        cmd_text = cmd_text.strip()
        _print(cmd_text)
        cmd_text, *args = cmd_text.split(' ')
        _print(f'cmd_text: {cmd_text}, input args: {args}', state=C['de'])
        if cmd_text in self.cmd_list:
            return self.execute(cmd_text, *args)
        else:
            raise Exception(f'Command not found: {cmd_text}😞', )
    
    def execute(self, text: str, *args):
        ex = self.cmd_dic[text][0]
        _print(f'command discrisption: {self.cmd_dic[text][1]}', state=C['de'])
        try:
            if len(args) > 0:
                res = ex(*args)
                _print(f'execute res: {res}', state=C['de'])
                return res
            else:
                return ex()   
        except Exception as e:
            res = 'err', f'Error: {e}'
            return res
        
    def run_analyze(self, cmd_text: str
                        , user_id: str):
        self.user_id = user_id
        try:
            if self.user_id in self.user_state:
                fn = self.user_state[user_id]
                del self.user_state[user_id]
                cmd_text, *args = cmd_text.split(' ')
                if len(args) > 0:
                    return fn(cmd_text, *args)
                else:
                    return fn(cmd_text)
            else:
                return self.analyze(cmd_text)
        except Exception as e:
            res = 'err', f'Error: {e}😅'
            return res
        
def _print(msg: str = '',
           state: str = C['inf'],):
    print(f"{W}{state} [Analysiser] | {msg}{W}")
        
if __name__ == "__main__":
    ca = CommandAnalysiser()
    inp = input('Enter command: ')
    print(ca.run(inp))

            
