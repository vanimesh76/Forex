import MetaTrader5 as mt5
from pandas import DataFrame, to_datetime
import time
from datetime import datetime
import pytz

mt5.initialize()
global df


def get_values(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H6, 0, 20)
    rates_frame = DataFrame(rates)

    rates_frame['time']=to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
    # rates_frame['rsi'] = get_rsi(rates_frame['close'], 14)

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
    lot = 0.02
    check = 0
    checks = 0
    buy_up = 0
    sell_up = 0
    buy = 1
    sell = 0
    hour_passed = True

    print(symbol)            

    while True:
        if hour_passed:
            t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
            if t.hour in (0,6,12,18):
                result_sell = Action(symbol, lot, sell)  #SELL Action
                result_buy = Action(symbol, lot, buy)  #BUY Action

                if checks == 1:
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close
                    if result_buy.comment == "Requote":
                        result_buy = Action_close(result_buy.order, symbol, buy, lot)
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment}")

                if check == 1:
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                    if result_sell.comment == "Requote":
                        result_sell = Action_close(result_sell.order, symbol, sell, lot)
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment}")

                print(f"Symbol-->{symbol} ||| Type-->Sell ||| Ticket_No-->{result_sell.order} ||| result_comment-->{result_sell.comment}")
                print(f"Symbol-->{symbol} ||| Type-->Buy ||| Ticket_No-->{result_buy.order} ||| result_comment-->{result_buy.comment}")

                check = 1
                checks = 1
                hour_passed = False

        if check == 1:
            pp = mt5.positions_get(ticket=result_buy.order)[0].profit
            if pp > 0.40:
                result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                if result_buy.comment == "Requote":
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment}")
                check = 0

        if checks == 1:
            pp = mt5.positions_get(ticket=result_sell.order)[0].profit
            if pp >= 0.40:
                result_sell = Action_close(result_sell.order, symbol, sell, lot)
                
                if result_sell.comment == "Requote":
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment}")
                checks = 0

        
        if check == 0 and checks == 0:
            t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
            print(f"Hour--->{t.hour}")
            if t.hour >= 0 and t.hour < 6:
                print(6*60*60 - (t.hour*60*60 + t.minute*60))
                time.sleep(6*60*60 - (t.hour*60*60 + t.minute*60))

            elif t.hour >= 6 and t.hour < 12:
                print(12*60*60 - (t.hour*60*60 + t.minute*60))
                time.sleep(12*60*60 - (t.hour*60*60 + t.minute*60))

            elif t.hour >= 12 and t.hour < 18:
                print(18*60*60 - (t.hour*60*60 + t.minute*60))
                time.sleep(18*60*60 - (t.hour*60*60 + t.minute*60))

            elif t.hour >= 18 and t.hour < 24:
                print(24*60*60 - (t.hour*60*60 + t.minute*60))
                time.sleep(24*60*60 - (t.hour*60*60 + t.minute*60))

            hour_passed = True


for symbol in ['EURGBP']:
    run(symbol)