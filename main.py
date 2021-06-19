# pip install requests
# pip install line-bot-sdk


# OpenWeatherMap,main関連
import os
import requests
import json
from datetime import datetime, timedelta, timezone


# LINE Messaging API(bot)関連
from linebot import LineBotApi
from linebot.models import TextSendMessage

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])


# OpenWeatherMapからのデータ取得
lat_Kobe_sta = '34.691138'
lon_Kobe_sta = '135.192433'
owm_key = os.environ['OWM_KEY']

url = 'http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={key}&units=metric'
url2 = 'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}&units=metric'

url = url.format(lat=lat_Kobe_sta, lon=lon_Kobe_sta, part='current,minutely,daily,alerts', key=owm_key)
url2 = url2.format(lat=lat_Kobe_sta, lon=lon_Kobe_sta, key=owm_key)

jsondata = requests.get(url).json()
jsondata2 = requests.get(url2).json()
tz = timezone(timedelta(hours=+9), 'JST')


# 天気を3種に分類する関数
def judge(weather, wind_speed):
    if (weather == 'Clear') or (weather == 'Clouds'):
        if wind_speed > 15:
            msg = '\n' + jst + ' 強風'
        else:
            msg = '\n' + jst + ' OK'
    else:
        msg = '\n' + jst + ' 雨等悪天候'

    return msg


# weather_main1
n = 0
message = '神戸駅\n'+'\n本日の外干しアドバイス\n'

for dat in jsondata['hourly']:
    n += 1
    jst = str(datetime.fromtimestamp(dat['dt'], tz))[11:-9]
    weather = dat['weather'][0]['main']
    wind_speed = dat['wind_speed']

    if n <= 12: #7:00実行/情報7:00～18:00
        judge_msg = judge(weather, wind_speed)
        message = message + judge_msg
    else:
        break


# weather_main2
n = 0
message = message + '\n' + '\n明日以降の外干しアドバイス\n'

for dat in jsondata2['list']:
    n += 1
    jst = str(datetime.fromtimestamp(dat['dt'], tz))[5:-9]
    weather = dat['weather'][0]['main']
    wind_speed = dat['wind']['speed']

    if n <= 8:
        continue
    elif (n % 8 > 4) or (n % 8 == 0):
        continue
    else:
        judge_msg = judge(weather, wind_speed)
        message = message + judge_msg

    if (n == 12) or (n == 20) or (n == 28):
        message = message + '\n'


# LINE Messaging API(bot)関連
def main():
    messages = TextSendMessage(message)
    line_bot_api.broadcast(messages=messages)

if __name__ == "__main__":
    main()