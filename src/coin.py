import requests
import yaml

class CryptoPrice:
    def __init__(self, 
                 api_key: str,
                 base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def get_crypto_price(self, coin_symbol: str):
        url = f"{self.base_url}/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        params = {"symbol": coin_symbol, "convert": "USD"}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            try:
                # 獲取幣種現在的價格
                coin_data = data["data"][coin_symbol]["quote"]["USD"]
                #四捨五入到小數點後兩位
                price = round(coin_data["price"], 2)
                # 獲取24小時變化百分比並四捨五入到小數點後兩位
                percent_change_24h = round(coin_data["percent_change_24h"], 2)
                return price, percent_change_24h
            except KeyError:
                raise Exception(f"KeyError: Coin symbol {coin_symbol} not found in response.")
        else:
            raise Exception(f"Fail to get crypto data: {response.status_code}, {response.text}")

    def display_price(self, coin_symbol: str):
        try:
            price, percent_change_24h = self.get_crypto_price(coin_symbol.upper())
            #回傳
            return 'msg', f"💰當前價格{coin_symbol.upper()}: ${price}\n⏰24h變化: {percent_change_24h}%"
        except Exception as e:
            return 'err', f"Error: {e}"
