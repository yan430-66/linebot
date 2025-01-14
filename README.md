```
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
                      _oo0oo_
                      o8888888o
                      88" . "88
                      (| -_- |)
                      0\  =  /0
                    ___/`---'\___
                  .' \\|     |// '.
                 / \\|||  :  |||// \
                / _||||| -:- |||||- \
               |   | \\\  - /// |   |
               | \_|  ''\---/''  |_/ |
               \  .-\__  '-'  ___/-. /
             ___'. .'  /--.--\  `. .'___
          ."" '<  `.___\_<|>_/___.' >' "".
         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
         \  \ `_.   \_ __\ /__ _/   .-` /  /
     =====`-.____`.___ \_____/___.-`___.-'=====
                       `=---='

       此專案被 南無BUG菩薩保佑，不當機，不報錯
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
```
程式設計期末報告
===
LINEBOT 工具箱
---
## 組員:
>C112156118 楊睿宏
>
>C112156132 陳孟暄
>
>C112156148 顏岑光
>
>C112156151 林  峰
>

## 簡介:

## 使用方法:
> [!CAUTION]  
> 免責聲明:
>
> 此程式所讀取訊息、圖片，皆為暫存使用，不對其長時間保存，因此不對使用者之訊息、圖片等個人資料負責。
>

> [!WARNING]  
> 注意事項:
>
> 
- 掃描此QR code，至 LINE APP 中，將機器人加為好友；直接進行對話即可使用。
![image](https://github.com/user-attachments/assets/0b7f1691-e3ee-487a-bec4-0e65a55ca1aa)

## 自行架設:
> [!NOTE]  
> 事前準備
>
> 需準備 Github、公開資料相關網站、Line Developers 帳號。
> 
> 複製項目地址
```bash
clone https://github.com/yan430-66/linebot
```
### 將cfg.yaml內對應之
>將API放入cfg.yaml
### python 安裝
>python 虛擬環境 建議python 版本 > 10
```
python -m venv myenv
myenv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install requirements.txt
python start.py -cfg ./cfg.yaml
# or open in debug mode
python start.py -debug
```

## 機器人功能:
###  1. 模型預測情緒
###  2. 加密貨幣價格查詢
###  3. 匯率轉換
###  4. 股票價格
###  5. 爬蟲關鍵字新聞
###  6. Youbike站點資訊查詢
###  7. 天氣資訊查詢
## 功能選單:
![image](https://github.com/user-attachments/assets/c9744738-0569-41c5-ae16-d16f74c46f16)
## 功能實際執行:
###  功能1. 模型預測情緒:
>有兩個version，第2個version :https://drive.google.com/drive/folders/1W_ggfWMN4e89t3mBuKM28m_Z1QKPwk3B?usp=drive_link
>
![image](https://github.com/user-attachments/assets/8b3f2cab-3677-4a6d-ad83-c5d8a71f8b51)
###  功能2. 加密貨幣價格查詢
![image](https://github.com/user-attachments/assets/d05e48c1-6d42-450c-8d3f-7be4e1bc3576)
###  功能3. 匯率轉換
![image](https://github.com/user-attachments/assets/f937f5be-1486-4aea-a742-64acce12abcc)
###  功能4. 股票價格
![image](https://github.com/user-attachments/assets/49b474b8-6c27-4724-8796-c5b3aa8996e4)
###  功能5. 爬蟲關鍵字新聞
![image](https://github.com/user-attachments/assets/a7342a1b-8fef-47fc-8abb-fdd5cb5610af)
###  功能6. Youbike站點資訊查詢
![image](https://github.com/user-attachments/assets/7166192c-eb31-4cc3-a640-1a4954bfcb04)
![image](https://github.com/user-attachments/assets/43e45d4d-59bd-469f-9afd-5f741e6e84de)
###  功能7. 天氣資訊查詢
![image](https://github.com/user-attachments/assets/827bcac8-be54-4897-a61a-62c11bb0f7fc)


## 公開資料:
### CoinMarketCap:https://coinmarketcap.com/
### xe:https://www.xe.com/currencyconverter/
### News API:https://newsapi.org/
### 交通部中央氣象屬:https://www.cwa.gov.tw/V8/C/W/OBS_Map.html

## 分工:
### 楊睿宏 : 整體框架、邏輯建構、天氣功能
### 陳孟暄 : 情感分析功能、情感分析模型、股票查詢功能、新聞抓取50%
### 顏岑光 : 加密貨幣價格查詢、Youbike站點資訊查詢、圖文選單、readme.md
### 林  峰 : 匯率轉換功能、新聞抓取50%、rq.txt
