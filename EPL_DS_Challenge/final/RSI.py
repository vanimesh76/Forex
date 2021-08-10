from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import time
import pandas_ta as pta
import threading

mt5.initialize()
def get_values(symbol):
    timezone = pytz.timezone("Etc/UTC")
    x = datetime.now()
    utc_from = datetime(x.year, x.month, x.day-1, tzinfo=timezone)
    utc_to = datetime(x.year, x.month, x.day+1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop(['tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
    rates_frame = rates_frame.drop(['high', 'low'], axis=1)
    return rates_frame

def get_rsi(close, lookback):
    ret = close.diff()
    
    up = []
    down = []
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
            down.append(0)
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com = lookback - 1, adjust = False).mean()
    down_ewm = down_series.ewm(com = lookback - 1, adjust = False).mean()
    rs = up_ewm/down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
    return rsi_df



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
        # dictt[symbol][signal] = 0
    except Exception as e:
        print("Action_close")
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

def slope(x1, y1, x2, y2):
    return (y2-y1)/(x2-x1)

def go(df):
    g = []
    for i in range(0, len(df)):
        if df.iloc[i].rsi >= 60.0:
            g.append(slope(0, df.iloc[i-5].rsi, 5, df.iloc[i].rsi))
        else:
            g.append(0)
    return g

def run(symbol):
    check = 0
    lot = 0.02
    while True:
        df = get_values(symbol)
        df['rsi'] = get_rsi(df['close'], 30)
        df['smaL']= df['rsi'].rolling(window=2).mean()
        df['slope'] = go(df)

        if df.iloc[-2].slope > 1.9 and df.iloc[-2].slope > 0.0 and df.iloc[-3].slope == 0.0 \
            and check == 0:
            buy_price = df.iloc[-2].close
            signal = 0 #SELL
            result = Action(symbol, lot, signal)
            print(f"Symbol-->{symbol} ||| Ticket_No-->{result.order}")
            check = 1  

        elif check == 1:
            
            signal = 1
            sell_price = df.iloc[-2].close
            pp = price_action(symbol, lot, buy_price, sell_price, mt5.ORDER_TYPE_SELL)

            if pp < -1.3:
                Action_close(result.order, symbol, signal, lot)
                check = 0

            if df.iloc[-2].rsi <= 41.0:
                Action_close(result.order, symbol, signal, lot)
                check = 0
        time.sleep(3)


for symbol in ['GBPUSD', 'USDJPY', 'CADJPY', 'EURUSD', 'EURGBP']:
    p2 = threading.Thread(target=run, args=(symbol,))
    p2.start()
