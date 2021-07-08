from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import time
import threading

def get_values(symbol):
    timezone = pytz.timezone("Etc/UTC")
    x = datetime.now()
    utc_from = datetime(2021, 6, 15, tzinfo=timezone)
    # utc_to = datetime(x.year, x.month, x.day+1, tzinfo=timezone)
    utc_to = datetime(x.year, x.month+1, 1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M30, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop(['open', 'high', 'low','tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')

    EMA = rates_frame['close'].ewm(span=100, adjust=False).mean()
    DEMA = 2*EMA - EMA.ewm(span=100, adjust=False).mean()
    rates_frame['dma'] = DEMA
    rates_frame['ll'] = rates_frame['close'].rolling(window=100).mean()
    return rates_frame

#close order
def Action_close(ticket_no, symbol, signal):
    a = [[mt5.symbol_info_tick(symbol).bid, mt5.ORDER_TYPE_SELL], [mt5.symbol_info_tick(symbol).ask, mt5.ORDER_TYPE_BUY]]
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
    dictt[symbol][signal] = 0



def Profit_checker(ticket_no, symbol, signal, dma):
    print(ticket_no)
    while True:
        try:
            order_status = mt5.positions_get(ticket=ticket_no)
            profit = order_status[0].profit
            if profit >= 0.30:
                Action_close(ticket_no, symbol, signal)
                break
            elif profit <= -0.50:
                Action_close(ticket_no, symbol, signal)
                break

            rates_frame = get_values(symbol)
            if signal == 0: #Buy Signal
                if rates_frame.iloc[-1].close < dma:
                    Action_close(ticket_no, symbol, signal)
                    break
            elif signal == 1: #Buy Signal
                if rates_frame.iloc[-1].close > dma:
                    Action_close(ticket_no, symbol, signal)
                    break
        except Exception as e:
            print(e)

def Action(symbol, lot, signal):
    symbol_info = mt5.symbol_info(symbol)

    a = [[mt5.ORDER_TYPE_BUY, mt5.symbol_info_tick(symbol).ask], [mt5.ORDER_TYPE_SELL, mt5.symbol_info_tick(symbol).bid]]
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
    time.sleep(2)
    return result

def price_action(symbol, lot, ask, bid, order_type):
    buy_profit=mt5.order_calc_profit(order_type,symbol,lot,ask,bid)
    return buy_profit

if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
global dictt
key = 0
dictt = {'EURUSD':[0, 0, 0.01, 'll'], 'GBPUSD':[0, 0, 0.01, 'll'], 'USDJPY':[0, 0, 0.01, 'll'], 'EURGBP':[0, 0, 0.01, 'll'],'USDCHF':[0, 0, 0.01, 'll'], 'CADJPY':[0, 0, 0.03, 'll']}

while True:
    for symbol in dictt:
        rates_frame = get_values(symbol)
        lot = dictt[symbol][2]


        if dictt[symbol][3] == 'll':
            sett = rates_frame.iloc[-1].ll
            ask=rates_frame.iloc[-2].ll
            bid=rates_frame.iloc[-1].close

        elif dictt[symbol][3] == 'dma':
            sett = rates_frame.iloc[-1].dma
            ask=rates_frame.iloc[-2].dma
            bid=rates_frame.iloc[-1].close

        if rates_frame.iloc[-2].close > sett and \
            rates_frame.iloc[-3].close < sett and \
            dictt[symbol][0] == 0 and \
            rates_frame.iloc[-1].close > rates_frame.iloc[-2].close:

            
            signal = 0
            order_type = mt5.ORDER_TYPE_SELL
            buy_profit = price_action(symbol, lot, ask, bid, order_type)
            
            if buy_profit > -0.40:
                print(buy_profit)
                result = Action(symbol, lot, signal)
                p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, sett))
                p1.start()
                dictt[symbol][0] = 1
                # dictt[symbol][1] = 0
            
        elif rates_frame.iloc[-2].close < sett and \
            rates_frame.iloc[-3].close > sett and \
            dictt[symbol][1] == 0 and\
            rates_frame.iloc[-1].close < rates_frame.iloc[-2].close:

            signal = 1
            # ask=rates_frame.iloc[-2].dma
            # bid=rates_frame.iloc[-1].close
            order_type = mt5.ORDER_TYPE_BUY
            buy_profit = price_action(symbol, lot, ask, bid, order_type)
            
            if buy_profit > -0.40: 
                print(buy_profit)
                result = Action(symbol, lot, signal)
                p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, sett))
                p1.start()
                dictt[symbol][1] = 1
                # dictt[symbol][0] = 0

    time.sleep(5)


