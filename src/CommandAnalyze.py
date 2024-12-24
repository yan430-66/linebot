from .color import C, W
from .sentiment import Sentiment
from .weather_api import Weather_clm
from .coin import CryptoPrice
from .currency import CurrencyConverter

class Command():
    def __init__(self, 
                 weather_api_key: str,
                 crypto_api_key: str,
                 crypto_base_url: str,
                 cc_api_key: str,
                 cc_base_url: str):
        
        self.user_state = {}
        self.crypto_api_key = crypto_api_key
        self.crypto_base_url = crypto_base_url
        self.weather = Weather_clm(weather_api_key)
        self.cc = CurrencyConverter(api_key=cc_api_key, base_url=cc_base_url)
        self.co =  CryptoPrice(api_key=self.crypto_api_key, base_url=self.crypto_base_url)
        self.se = Sentiment()
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

    def chosise_3(self,):
        self.user_state[self.user_id] = self._get_converter # = {user_id: self._converter}
        res = 'msg', f'Enter the amount and currency conversion (e.g., 100 USD to EUR): '
        return res

    def chosise_1(self,):
        self.user_state[self.user_id] = self.sentiment
        return 'msg', f'請傳送一則訊息讓 module1 判斷。'
    
    def chosise_2(self,):
        self.user_state[self.user_id] = self.coin
        return 'msg', f'輸入要查詢之加密貨幣(e.g., BTC, ETH): '
    
    def coin(self, msg: str):
        return self.co.display_price(msg)
    
    def sentiment(self, msg: str):
        return self.se.predict_sentiment(msg)

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
                 weather_api_key: str,):
        super(Command, self).__init__(weather_api_key-weather_api_key,)

    def analyze(self, cmd_text: str): 
        cmd_text = cmd_text.strip()
        _print(cmd_text)
        cmd_text, *args = cmd_text.split(' ')
        _print(f'cmd_text: {cmd_text}, input args: {args}')
        if cmd_text in self.cmd_list:
            return self.execute(cmd_text, *args)
        else:
            raise Exception(f'Command not found: {cmd_text}')
    
    def execute(self, text: str, *args):
        ex = self.cmd_dic[text][0]
        _print(f'command discrisption: {self.cmd_dic[text][1]}', state=C['de'])
        try:
            if len(args) > 0:
                res = ex(*args)
                _print(f'execute res: {res}')
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
            res = 'err', f'Error: {e}'
            return res
        
def _print(msg: str = '',
           state: str = C['inf'],):
    print(f"{W}{state} [Analysiser] | {msg}{W}")
        
if __name__ == "__main__":
    ca = CommandAnalysiser()
    inp = input('Enter command: ')
    print(ca.run(inp))

            