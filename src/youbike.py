import requests
import pandas as pd
import csv
from urllib.parse import quote

class YouBike:
    def __init__(self):
        self.api_url = "https://apis.youbike.com.tw/json/station-yb2.json"
        self.base_url = "https://www.google.com/maps/search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.csv_file = "youbike_stations.csv"
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

    def fetch_youbike_data(self):
        response = requests.get(self.api_url, headers=self.headers)
        if response.status_code == 200:
            try:
                return 'msg', response.json()
            except ValueError as e:
                return 'err', f"解析 JSON 資料時出現錯誤: {e}"
        else:
            return 'err', f"請求失敗，狀態碼: {response.status_code}"

    def parse_area_input(self, input_value: str):
        return input_value.strip()

    def filter_data_by_region_area(self, data, region: str, area: str):
        area_code = self.get_area_code(region)
        if not area_code:
            return 'err', f"找不到對應的地區代碼: {region}"

        filtered_data = [station for station in data if station.get('area_code') == area_code and station.get('district_tw') == area]
        if not filtered_data:
            return 'err', "沒有符合條件的資料"

        return 'msg', filtered_data

    def display_stations_by_area(self, city_name: str, area: str):
        fetch_status, data = self.fetch_youbike_data()
        if fetch_status == 'err':
            return 'err', data

        filter_status, filtered_data = self.filter_data_by_region_area(data, city_name, area)
        if filter_status == 'err':
            return 'err', filtered_data

        station_names = [station.get('name_tw', '未知站點') for station in filtered_data]
        if station_names:
            message = f"區域 {area} 的所有站點名稱如下:\n" + "\n".join(station_names)
            return 'msg', message
        return 'err', f"找不到區域 {area} 的站點資料"

    def display_station_info(self, city_name: str, area: str, station: str):
        fetch_status, data = self.fetch_youbike_data()
        if fetch_status == 'err':
            return 'err', data

        filter_status, filtered_data = self.filter_data_by_region_area(data, city_name, area)
        if filter_status == 'err':
            return 'err', filtered_data

        for station_data in filtered_data:
            if station_data.get('name_tw') == station:
                available_spaces = station_data.get('available_spaces', '無資料')
                address = station_data.get('address_tw', '無地址')
                google_maps_link = "https://www.google.com/maps/search/?api=1&query="+address
                message = (
                    f"站點名稱: {station}\n"
                    f"可用數量: {available_spaces}\n"
                    f"地址: {address}\n"
                    f"📍Google Maps 鏈結: {google_maps_link}"
                )
                return 'msg', message

        return 'err', f"找不到站點 {station}"

    def get_area_code(self, city_name):
        return next((code for code, name in self.area_code_mapping.items() if name == city_name), None)

    def address_to_google_maps_url(self, address):
        encoded_address = quote(address)
        return f"{self.base_url}{encoded_address}"

if __name__ == "__main__":
    youbike = YouBike()

    region = "台北"
    area = "信義區"

    res_type, res_message = youbike.display_stations_by_area(region, area)
    print(res_message)

    station_name = "市府轉運站"
    res_type, res_message = youbike.display_station_info(region, area, station_name)
    print(res_message)
