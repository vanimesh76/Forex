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
    utc_to = datetime(x.year, x.month+1, x.day+1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop([ 'high', 'low','tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')

    EMA = rates_frame['close'].ewm(span=100, adjust=False).mean()
    DEMA = 2*EMA - EMA.ewm(span=100, adjust=False).mean()
    rates_frame['dma'] = DEMA
    rates_frame['ll'] = rates_frame['close'].rolling(window=100).mean()
    return rates_frame

#close order
def Action_close(ticket_no, symbol, signal, lot):
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



def Profit_checker(ticket_no, symbol, signal, lot):
    print(ticket_no)
    while True:
        try:
            order_status = mt5.positions_get(ticket=ticket_no)
            profit = order_status[0].profit
            print(profit)
            if profit >= 0.30:
                Action_close(ticket_no, symbol, signal, lot)
                break
            elif profit <= -1.0:
                Action_close(ticket_no, symbol, signal, lot)
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



def go(symbol, buy_counter, sell_counter):
    print(symbol)
    while True:
        rates_frame = get_values(symbol)
        lot = dictt[symbol][2]

        sett = rates_frame.iloc[-1].ll
        ask=rates_frame.iloc[-2].ll
        bid=rates_frame.iloc[-1].close

        if rates_frame.iloc[-2].close > sett and \
            rates_frame.iloc[-2].open < sett and \
            dictt[symbol][0] == 0:
            buy_counter = 1

        if buy_counter == 1 and rates_frame.iloc[-2].close > sett and rates_frame.iloc[-2].open > sett:
            signal = 0
            # order_type = mt5.ORDER_TYPE_SELL
            # buy_profit = price_action(symbol, lot, ask, bid, order_type)
            
            # if buy_profit > -0.40:
            # print(buy_profit)
            result = Action(symbol, lot, signal)
            p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, lot))
            p1.start()
            dictt[symbol][0] = 1
            buy_counter = 0
            
        if rates_frame.iloc[-2].close < sett and \
            rates_frame.iloc[-2].open > sett and \
            dictt[symbol][1] == 0:
            sell_counter = 1

        if sell_counter == 1 and rates_frame.iloc[-2].close < sett and rates_frame.iloc[-2].open < sett:
            signal = 1
            result = Action(symbol, lot, signal)
            p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, lot))
            p1.start()
            dictt[symbol][1] = 1
            sell_counter = 0

    time.sleep(90)


def go_test(symbol, buy_counter, sell_counter):
    row = get_values(symbol)[100:]
    for index, rates_frame in row.iterrows():
        # print(index)
        # print(rates_frame.ll,rates_frame.ll,rates_frame.close)
        # break
        

        lot = dictt[symbol][2]

        sett = rates_frame.ll
        ask=rates_frame.ll
        bid=rates_frame.close

        if rates_frame.close > sett and \
            rates_frame.open < sett and \
            dictt[symbol][0] == 0:
            buy_counter = 1

        if buy_counter == 1 and rates_frame.close > sett and rates_frame.open > sett:
            signal = 0
            # order_type = mt5.ORDER_TYPE_SELL
            # buy_profit = price_action(symbol, lot, ask, bid, order_type)
            
            # if buy_profit > -0.40:
            # print(buy_profit)
            # result = Action(symbol, lot, signal)
            # p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, lot))
            # p1.start()
            # dictt[symbol][0] = 1
            print("*"*20+"BUY"+"*"*20)
            print(index)
            print(rates_frame.close)
            buy_counter = 0
            
        if rates_frame.close < sett and \
            rates_frame.open > sett and \
            dictt[symbol][1] == 0:
            sell_counter = 1

        if sell_counter == 1 and rates_frame.close < sett and rates_frame.open < sett:
            # signal = 1
            # result = Action(symbol, lot, signal)
            # p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, lot))
            # p1.start()
            # dictt[symbol][1] = 1
            print("*"*20+"SELL"+"*"*20)
            print(index)
            print(rates_frame.close)
            sell_counter = 0

    # time.sleep(90)

mt5.initialize()
global dictt
key = 0
dictt = {'EURUSD':[0, 0, 0.02, 'll']}#, 'GBPUSD':[0, 0, 0.02, 'll'], 'USDJPY':[0, 0, 0.02, 'll'], 'EURGBP':[0, 0, 0.02, 'll'],'USDCHF':[0, 0, 0.02, 'll'], 'CADJPY':[0, 0, 0.03, 'll']}

buy_counter = 0
sell_counter = 0

for symbol in dictt:
    go_test(symbol, buy_counter, sell_counter)
    # p2 = threading.Thread(target=go_test, args=(symbol, buy_counter, sell_counter))
    # p2.start()

