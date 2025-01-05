import yfinance as yf
from datetime import datetime

class Stock:
    def __init__(self):
        self.stock_data = None

    def fetch_stock_data(self, stock_code: str, start_date: str, end_date: str):
        try:
            print(f"Fetching data for {stock_code} from {start_date} to {end_date}")
            stock = yf.download(stock_code, start=start_date, end=end_date)
            if stock.empty:
                return 'msg', "指定日期範圍內沒有找到數據。", None
            self.stock_data = stock
            return 'msg', f"成功取得 {stock_code} 的股票數據。", stock
        except OSError as e:
            return 'err', f"I/O 錯誤: {e}", None

    def parse_date_input(self, date_input: str):
        try:
            date = datetime.strptime(date_input.replace('/', '-'), '%Y-%m-%d')
            return 'msg', f"成功解析日期: {date.strftime('%Y-%m-%d')}", date.strftime('%Y-%m-%d')
        except ValueError:
            return 'err', "日期格式無效。請使用 YYYY-MM-DD 或 YYYY/MM/DD 格式。", None

    def get_high_low_info(self):
        if self.stock_data is None:
            return None, None, None, None

        high_prices = self.stock_data['High'].to_numpy()
        high_dates = self.stock_data.index.strftime('%Y-%m-%d').to_numpy()
        low_prices = self.stock_data['Low'].to_numpy()
        low_dates = self.stock_data.index.strftime('%Y-%m-%d').to_numpy()

        highest_index = high_prices.argmax()
        lowest_index = low_prices.argmin()

        highest = float(high_prices[highest_index])
        highest_date = high_dates[highest_index]
        lowest = float(low_prices[lowest_index])
        lowest_date = low_dates[lowest_index]

        return highest, highest_date, lowest, lowest_date

    def display_stock_info(self, stock_code: str, start_date_input: str, end_date_input: str):
        # 解析開始日期
        start_status, start_msg, start_date = self.parse_date_input(start_date_input)
        if start_date is None:
            print(f"Parsing start date failed: {start_msg}")
            return 'err', start_msg

        # 解析結束日期
        end_status, end_msg, end_date = self.parse_date_input(end_date_input)
        if end_date is None:
            print(f"Parsing end date failed: {end_msg}")
            return 'err', end_msg

        # 取得股票數據
        fetch_status, fetch_msg, stock_data = self.fetch_stock_data(stock_code, start_date, end_date)
        if fetch_status == 'err' or stock_data is None:
            print(f"Fetching stock data failed: {fetch_msg}")
            return fetch_status, fetch_msg

        # 分析最高價和最低價
        highest, highest_date, lowest, lowest_date = self.get_high_low_info()
        if highest is None:
            print("Not enough data to analyze high and low prices.")
            return 'msg', "沒有足夠的數據來分析最高價和最低價。"

        # 格式化顯示訊息
        message = (
            f"股票代碼: {stock_code}\n"
            f"日期範圍: {start_date} 至 {end_date}\n"
            f"{stock_data}\n"
            f"最高價: {highest:.2f} 元 (日期: {highest_date})\n"
            f"最低價: {lowest:.2f} 元 (日期: {lowest_date})"
        )
        print(f"Returning message: {message}")
        return 'msg', message