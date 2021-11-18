import MetaTrader5 as mt5
import pandas as pd
import time
import pytz
from datetime import datetime
import numpy as np

mt5.initialize()


def get_values(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 50)
    rates_frame = pd.DataFrame(rates)

    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
    
    rates_frame['sma']= rates_frame['close'].rolling(window=10).mean()

    return rates_frame


def Action_close(ticket_no, symbol, signal, lot):
    try:
        a = [[mt5.symbol_info_tick(symbol).ask, mt5.ORDER_TYPE_BUY], [mt5.symbol_info_tick(symbol).bid, mt5.ORDER_TYPE_SELL]]
        position_id=ticket_no
        price = a[signal][0]
        deviation=1000
        request={
            "action": mt5.TRADE_ACTION_DEAL,    
            "symbol": symbol,
            "volume": lot,
            "type": a[signal][1],
            "position": position_id,
            "price": price,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result=mt5.order_send(request)
        return result
    except Exception as e:
        print("Action_close_Error")
        print(e)

def Action(symbol, lot, signal):
    try:
        symbol_info = mt5.symbol_info(symbol)

        a = [[mt5.ORDER_TYPE_SELL, mt5.symbol_info_tick(symbol).bid], [mt5.ORDER_TYPE_BUY, mt5.symbol_info_tick(symbol).ask]]
        price = a[signal][1]
        deviation = 200
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": a[signal][0],
            "price": price,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(request)
        return result
    except Exception as e:
        print("Action")
        print(e)


def run(symbol):
    check = 0
    lot = 0.02
    buy_check = 0
    sell_check = 0
    buy_up = 0
    sell_up = 0
    order_time = 0

    buy = 1
    sell = 0
 
    print(symbol)
    hour_passed = True

    while True:
        a = get_values(symbol)
        if hour_passed:
            
            order_time = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))

            if  order_time.hour <= 1 and a.iloc[-2].close < a.iloc[-2].sma and a.iloc[-3].close > a.iloc[-2].close and sell_check == 0:   

                result_sell = Action(symbol, lot, sell)
                print(f"Symbol-->{symbol} ||| Type-->Sell  ||| Ticket_No-->{result_sell.order}")

                sell_check = 1

                buy_check = 0
                hour_passed = False

            if order_time.hour <= 1 and a.iloc[-2].close > a.iloc[-2].sma and a.iloc[-3].close < a.iloc[-2].close and buy_check == 0:

                result_buy = Action(symbol, lot, buy)
                print(f"Symbol-->{symbol} ||| Type-->Buy ||| Ticket_No-->{result_buy.order} ||| result_comment-->{result_buy.comment}")
                buy_check = 1

                sell_check = 0

                hour_passed = False

            #############################################################

        t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
        if t.hour == 23 and sell_check == 1:
            result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
            
            if result_sell.comment == "Requote":
                result_sell = Action_close(result_sell.order, symbol, sell, lot)
                print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment} ||| Requoted")
            else:
                print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment}")
            sell_check = 0

            hour_passed = True


        if t.hour == 23 and buy_check == 1:
            result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

            if result_buy.comment == "Requote":
                result_buy = Action_close(result_buy.order, symbol, buy, lot)
                print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment} ||| Requoted")
            else:
                print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment}")  
            buy_check = 0

            hour_passed = True


        print(f"Sleep Time-->{((60*60 - t.minute*60) + 1)}")
        time.sleep((60*60 - t.minute*60) + 1)

for symbol in ['GBPUSD']:
    run(symbol)