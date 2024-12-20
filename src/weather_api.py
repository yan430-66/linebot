import requests
import pandas as pd
import yaml
class Weather_clm:
    def __init__(self, api_key: str):
        self.url_dic = self.load_config()
        self.api_key = api_key

    def load_config(self):
        with open('./src/data_url/url.yaml', "r", encoding="utf-8") as yaml_file:
            loaded_config = yaml.safe_load(yaml_file)
        return loaded_config

    def url_requests(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            raise Exception(f"Fail to get weather data: {response.status_code}, {response.text}")

    def __data(self, 
                url: str,
                area: str = None):
        
        data = self.url_requests(url)
        MainData = data["records"]["Locations"][0]["Location"]
        res = ""
        for i in MainData:
            if area == i["LocationName"]:
                value = i["WeatherElement"][9]['Time'][0]['ElementValue'][0]["WeatherDescription"]
                InfoName=i["WeatherElement"][9]["ElementName"]
                res += f"{i['LocationName']}:{InfoName} \n {value}\n\n"
                break
            elif area == None:
                value = i["WeatherElement"][9]['Time'][0]['ElementValue'][0]["WeatherDescription"]
                InfoName=i["WeatherElement"][9]["ElementName"]
                res += f"{i['LocationName']}:{InfoName} \n {value}\n\n"

        return 'msg', res
    
    def get_weather(self, 
                    region: str,
                    area: str = None):
        try:
            region = region.replace("台", "臺")
            url = self.url_dic[region] + self.api_key
            msg, res = self.__data(url, area)
            return msg, res
        except KeyError as e:
            raise Exception(f"KeyError: {e}")
        except Exception as e:
            raise Exception(f"Exception: {e}")
        # region = region.replace("台", "臺")
        # url = self.url_dic[region] + self.api_key
        # msg, res = self.__data(url, area)
        # return msg, res
