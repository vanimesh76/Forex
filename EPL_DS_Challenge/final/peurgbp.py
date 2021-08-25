from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import time
import pandas_ta as pta
import threading

mt5.initialize()
global df

def get_values(symbol):
    timezone = pytz.timezone("Etc/UTC")
    x = datetime.now()
    utc_from = datetime(x.year, x.month, x.day-1, tzinfo=timezone)
    utc_to = datetime(x.year, x.month, x.day+1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M2, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop(['tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['clsma']= rates_frame['close'].rolling(window=8).mean()
    rates_frame['smaC']= rates_frame['clsma'].rolling(window=8).mean()


    rates_frame['clsma']= rates_frame['open'].rolling(window=8).mean()
    rates_frame['smaO']= rates_frame['clsma'].rolling(window=8).mean()

    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
    rates_frame = rates_frame.drop(['high', 'low', 'clsma'], axis=1)
    return rates_frame



def Action_close(ticket_no, symbol, signal, lot):
    try:
        a = [[mt5.symbol_info_tick(symbol).ask, mt5.ORDER_TYPE_BUY], [mt5.symbol_info_tick(symbol).bid, mt5.ORDER_TYPE_SELL]]
        position_id=ticket_no
        price = a[signal][0]
        deviation=200
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
            "type_filling": mt5.ORDER_FILLING_RETURN,
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
        deviation = 1000
        
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
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        result = mt5.order_send(request)
        return result
    except Exception as e:
        print("Action")
        print(e)

def price_action(symbol, lot, ask, bid, order_type):
    buy_profit=mt5.order_calc_profit(order_type,symbol,lot,ask,bid)
    return buy_profit

def follow(lot, signal, symbol, ticket, buy_price, order_type):
    cl = buy_price
    op = df.iloc[-2].open
    while True:
        # if df.iloc[-2].close != cl or df.iloc[-2].open != op:
        sell_price = df.iloc[-1].close
        pp = price_action(symbol, lot, buy_price, sell_price, order_type)
        if pp >= 0.10:
            result = Action_close(ticket, symbol, signal, lot)
            print(f"Close  Symbol-->{symbol} ||| result_comment-->{result.comment}")
            if result.comment == "Requote":
                result = Action_close(ticket, symbol, signal, lot)
                print(f"Close  Symbol-->{symbol} ||| result_comment-->{result.comment} ||| Requoted")
                print("Re-Quoted")
                pass
            else:
                break


def run(symbol):
    check = 0
    lot = 0.02
    cl = df.iloc[-2].close
    op = df.iloc[-2].open
    check = 0
    checks = 0
    print(symbol)
    while True:
        if df.iloc[-2].close != cl or df.iloc[-2].open != op:
            if df.iloc[-2].smaC < df.iloc[-2].smaO and check == 0:
                cl = df.iloc[-2].close
                op = df.iloc[-2].open
                signal = 0 #SELL
                result = Action(symbol, lot, signal)
                p2 = threading.Thread(target=follow, args=(lot, signal, symbol, result.order, result.price, mt5.ORDER_TYPE_SELL))
                p2.start()
                print(f"Symbol-->{symbol} ||| Ticket_No-->{result.order}")
                check = 1
                checks = 0
            elif df.iloc[-2].smaC > df.iloc[-2].smaO and checks == 0:
                cl = df.iloc[-2].close
                op = df.iloc[-2].open
                signal = 1 #BUY
                result = Action(symbol, lot, signal)
                p3 = threading.Thread(target=follow, args=(lot, signal, symbol, result.order, result.price, mt5.ORDER_TYPE_BUY))
                p3.start()
                print(f"Symbol-->{symbol} ||| Ticket_No-->{result.order}")
                checks = 1
                check = 0


def data_fetch(symbol):
    global df
    while True:
        df = get_values(symbol)


for symbol in ['EURGBP']:#, 'USDJPY', 'CADJPY', 'EURUSD', 'EURGBP']:
    df = get_values(symbol)
    p5 = threading.Thread(target=data_fetch, args=(symbol,))
    p5.start()
    p2 = threading.Thread(target=run, args=(symbol,))
    p2.start()


#EURGBP
#When reaching up wait for the AO to turn red when RSI above 60 and wait for Either RSI to fall below 60 or AO to turn RED for 
#enough candles Initiate Sell Signal

#BUY_Signal when RSI crosses Above 40 mark wait for it to reach 60

#-215.66
