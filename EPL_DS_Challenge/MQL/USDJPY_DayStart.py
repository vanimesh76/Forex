import MetaTrader5 as mt5
import pandas as pd
import time
import pytz
from datetime import datetime
from math import modf

mt5.initialize()


def get_values(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 10)
    rates_frame = pd.DataFrame(rates)

    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')


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
    lot = 0.03
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
        if hour_passed:
            a = get_values(symbol)
            if a.iloc[-2].name.hour == 3:
                if (a.iloc[-5].close - a.iloc[-2].close) <= -0.060:                
                    result_buy = Action(symbol, lot, buy)
                    print(f"Symbol-->{symbol} ||| Type-->Buy ||| Ticket_No-->{result_buy.order} ||| result_comment-->{result_buy.comment}")
                    buy_up = 1
                    buy_check = 1

                    sell_check = 0

                elif (a.iloc[-5].close - a.iloc[-2].close) >= 0.060:                
                    result_sell = Action(symbol, lot, sell)
                    print(f"Symbol-->{symbol} ||| Type-->Sell  ||| Ticket_No-->{result_sell.order} ||| result_comment-->{result_sell.comment}")
                    sell_up = 1
                    sell_check = 1

                    buy_check = 0

            if a.iloc[-2].name.hour == 0:
                if sell_check == 1 and sell_up == 1:
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                    
                    if result_sell.comment == "Requote":
                        result_sell = Action_close(result_sell.order, symbol, sell, lot)
                        print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment}")
                    sell_up = 0
                    sell_check = 0

                if buy_check == 1 and buy_up == 1:
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                    if result_buy.comment == "Requote":
                        result_buy = Action_close(result_buy.order, symbol, buy, lot)
                        print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment}")
                    buy_up = 0
                    buy_check = 0



            order_time = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3')).hour
            hour_passed = False

        if sell_check == 1 and sell_up == 1:
            if mt5.positions_get(ticket=result_sell.order)[0].profit >= 4.0:
                result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                
                if result_sell.comment == "Requote":
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)
                    print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment}")
                sell_up = 0

            elif a.iloc[-2].name.hour == 0:
                result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                
                if result_sell.comment == "Requote":
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)
                    print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment}")
                sell_up = 0
        

        if buy_check == 1 and buy_up == 1:
            if mt5.positions_get(ticket=result_buy.order)[0].profit >= 4.0:
                result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                if result_buy.comment == "Requote":
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment}")
                buy_up = 0

            elif a.iloc[-2].name.hour == 0:
                result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                if result_buy.comment == "Requote":
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment}")
                buy_up = 0

        t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
        if order_time == t.hour:
            print(f"SLeep Time-->{((60*60 - t.minute*60) + 1)}")
            time.sleep((60*60 - t.minute*60) + 1)
        
        if order_time != t.hour:
            order_time = t.hour
            hour_passed = True




for symbol in ['USDJPY']:
    run(symbol)