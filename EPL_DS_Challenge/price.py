import requests
import time
import numpy as np
import math
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz

def telegram_bot_sendtext(bot_message):
    try:
    
        bot_token = '1789310123:AAHiV-IiAML2uNvtyeeCp6fBIXOpisR4_JM'
        bot_chatID = '220684438'
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()
    except:
        pass
    

# test = telegram_bot_sendtext("Testing Telegram bot")
# print(test)


def calc(curr):
    try:
        print(curr)
        pd.set_option('display.max_columns', 500) # number of columns to be displayed
        pd.set_option('display.width', 1500)      # max table width to display

        # establish connection to MetaTrader 5 terminal
        if not mt5.initialize():
            print("initialize() failed, error code =",mt5.last_error())
            quit()

        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
        x = datetime.now()
        utc_from = datetime(2021, 4, 1, tzinfo=timezone)
        utc_to = datetime(x.year, x.month, x.day+1, tzinfo=timezone)
        # rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_M30, utc_from,75)
        rates = mt5.copy_rates_range(curr, mt5.TIMEFRAME_M30, utc_from, utc_to)

        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()

        rates_frame = pd.DataFrame(rates)
        # convert time in seconds into the datetime format
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        # rates_frame = rates_frame.set_index('time')

        # print(len(rates_frame['close']))
        rates_frame['ll'] = rates_frame['close'].rolling(window=100).mean()
        sen(curr, rates_frame)
    except:
        pass

def sen(curr, rates_frame):
    try:
        c = 0
        df = rates_frame.iloc[-147:]
        for index, row in df.iterrows():
            try:
                if row['close'] > row['ll'] and rates_frame.iloc[index+1]['close'] < row['ll']:
                    a = datetime.now() - rates_frame.iloc[index]['time']
                    if a.seconds <= 1000:
                        c+= 1
                elif row['close'] < row['ll'] and rates_frame.iloc[index+1]['close'] > row['ll']:
                    a = datetime.now() - rates_frame.iloc[index]['time']
                    if a.seconds <= 1000:
                        c += 1
            except:
                pass
        print(c)
        if c:
            telegram_bot_sendtext(curr+" Alert")
    except:
        pass


curr = ["GBPUSD", "USDJPY"]#,"EURUSD","EURGBP", "AUDUSD", "AUDJPY", "AUDCAD", "USDJPY"]
while True:
    try:
        for i in curr:
            calc(i)
        time.sleep(900)
    except:
        pass