import pandas as pd
import requests
import csv
import os
from urllib.parse import quote
class YouBike:
    def __init__(self):
        self.area_code_mapping = {
            '00': '台北',
            '0A': '苗栗',
            '05': '新北',
            '07': '桃園',
            '09': '新竹市',
            '0B': '新竹縣',
            '01': '台中',
            '08': '嘉義市',
            '11': '嘉義縣',
            '12': '高雄',
            '13': '台南',
            '14': '屏東縣',
            '10': '新竹科學園區',
        }
        self.url = "https://apis.youbike.com.tw/json/station-yb2.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.csv_file = f"youbike_stations.csv"

    def get_area_code(self, city_name):
        for code, name in self.area_code_mapping.items():
            if name == city_name:
                return code
        return None

    def get_youbike_data(self, city_name):
        response = requests.get(self.url, headers=self.headers)

        # 檢查請求是否成功
        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError as e:
                print(f"解析 JSON 資料時出現錯誤: {e}")
                data = []
        else:
            print(f"請求失敗，狀態碼: {response.status_code}")
            data = []

        if data:
            area_code = self.get_area_code(city_name)
            if area_code:
                filtered_data = [station for station in data if station.get('area_code') == area_code]

                if filtered_data:
                    
                    fieldnames = filtered_data[0].keys()

                    # 寫入 CSV 檔案
                    with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        for station in filtered_data:
                            writer.writerow(station)

                    print(f"資料已成功寫入 {self.csv_file}")

                else:
                    print("沒有符合條件的資料")
            else:
                print(f"找不到對應的地區代碼: {city_name}")
        else:
            print("沒有可用的資料來生成 CSV 檔案")

    # 定義將地址轉換為 Google Maps URL 的函數
    def address_to_google_maps_url(address):
        base_url = "https://www.google.com/maps/search/"
        encoded_address = quote(address)
        full_url = f"{base_url}{encoded_address}"
        return full_url
    
    def get_station_csv(self, district_tw_input):
        res = ''
        self.district_tw_input = district_tw_input
        # 讀取 CSV 檔案
        df = pd.read_csv(self.csv_file)
        # 假設 CSV 檔案中有 'district_tw', 'name_tw', 'available_spaces' 和 'address_tw' 四個欄位
        stations = df[['district_tw', 'name_tw', 'available_spaces', 'address_tw']]
        # 查找並顯示該區域的所有站點名稱
        self.district_stations = stations[stations['district_tw'] == district_tw_input]
        if not self.district_stations.empty:
            res += f"區域 {self.district_tw_input} 的所有站點名稱如下: "
            district_tw_input = self.district_stations
            for name in district_tw_input['name_tw']:
                res += f'{name}\n '
        return 'msg', res

    def get_station_info(self, name_tw_input):
        res = ''
        if not self.district_stations.empty:
            station_info = self.district_stations[self.district_stations['name_tw'] == name_tw_input]
            if not station_info.empty:
                available_spaces = station_info.iloc[0]['available_spaces']
                address_tw = station_info.iloc[0]['address_tw']
                google_maps_link = self.address_to_google_maps_url(address_tw)
                res += f" {name_tw_input} 的可用數量為: {available_spaces}"
                res += f"Google Maps 鏈結: {google_maps_link}"
                return 'msg', res
            else:
                res += f"找不到站點 {name_tw_input}"
                return 'msg', res
        else:
            res += f"找不到區域 {self.district_tw_input}"
            return 'msg', res


if __name__ == "__main__":
    youbike = YouBike()
    youbike.get_youbike_data("台北")
    res1, res2 = youbike.get_station_csv("信義區")
    print(res2)
    r1, r2 = youbike.get_station_info("信義區")
    print(r2)