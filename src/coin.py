import requests
import yaml

class CryptoPrice:
    def __init__(self, config_path: str = './cfg.yaml'):
        config = self.load_config(config_path)
        self.api_key = config['CoinMarketCapAPI_KEY']
        self.base_url = config['CoinMarketCapAPI_BASE_URL']

    def load_config(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as yaml_file:
            loaded_config = yaml.safe_load(yaml_file)
        return loaded_config

    def get_crypto_price(self, coin_symbol: str):
        url = f"{self.base_url}/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        params = {"symbol": coin_symbol, "convert": "USD"}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            try:
                coin_data = data["data"][coin_symbol]["quote"]["USD"]
                price = round(coin_data["price"], 2)
                percent_change_24h = round(coin_data["percent_change_24h"], 2)
                return price, percent_change_24h
            except KeyError:
                raise Exception(f"KeyError: Coin symbol {coin_symbol} not found in response.")
        else:
            raise Exception(f"Fail to get crypto data: {response.status_code}, {response.text}")

    def display_price(self, coin_symbol: str):
        try:
            price, percent_change_24h = self.get_crypto_price(coin_symbol.upper())
            return 'msg', f"當前價格{coin_symbol.upper()}: ${price}\n24h變化: {percent_change_24h}%"
        except Exception as e:
            return 'msg', f"Error: {e}"