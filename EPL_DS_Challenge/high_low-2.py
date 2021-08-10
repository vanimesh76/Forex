from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import time
import threading

global q
q = 0

mt5.initialize()
def get_values(symbol):
    timezone = pytz.timezone("Etc/UTC")
    x = datetime.now()
    utc_from = datetime(2021, 6, 30, tzinfo=timezone)
    utc_to = datetime(x.year, x.month+1, x.day+1, tzinfo=timezone)
    # utc_to = datetime(x.year, x.month+1, 1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop(['high', 'low','tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')

    return rates_frame

def get_values_1(symbol):
    try:
        timezone = pytz.timezone("Etc/UTC")
        x = datetime.now()
        utc_from = datetime(x.year, x.month, x.day-1, tzinfo=timezone)
        utc_to = datetime(x.year, x.month+1, x.day+1, tzinfo=timezone)
        # utc_to = datetime(x.year, x.month+1, 1, tzinfo=timezone)
        rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M30, utc_from, utc_to)

        rates_frame = pd.DataFrame(rates)
        rates_frame = rates_frame.drop(['high', 'low','tick_volume', 'spread', 'real_volume'], axis=1)
        # convert time in seconds into the datetime format
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame = rates_frame.set_index('time')

        return rates_frame
    except Exception as e:
        print("get_values_1")
        print(e)

def dry_run(symbol, a, c):
    df = a.iloc[c:]
    up = 0
    newHigh = 0
    newLow = 0
    oldHigh = 0
    oldLow = 0
    check = 0
    final = 0
    highest = 0

    row = a.iloc[c:].iloc[0]
    if row.close > row.open:
        newHigh = row.close
        newLow = row.open
    else:
        newHigh = row.open
        newLow = row.close
        
    oldLow = 0
    oldHigh = newHigh
        
    #for a rising market
    for index, row in df.iterrows():
        if row.close > newHigh:
            if oldLow == 0:
                oldLow = newLow
            newHigh = row.close
            newLow = row.open
            
        if highest < newHigh:
            highest = newHigh

        if row.close > oldHigh and row.close > row.open and check == 0:
            if final == 1: #entering market after second candle consiqutively is up
                check = 1 #keeps note of shot fired already i.e. trade taken already for that oldHigh
                #Buy Signal

                oldLow = 0
            final = final+1
            
        if row.close < newHigh and row.close < newLow:
            newLow = row.close
            newHigh = row.open  #Check and Final will be automatically set to zero only when the trades close, NOT HERE
            if check == 1:
                oldHigh = newHigh
                timee = index
                check = 0    

            
        elif row.close < newHigh and row.open < row.close:
            newLow = row.open
            newHigh = row.close
        elif row.close < newHigh and row.open > row.close:
            newLow = row.close
            newHigh = row.open
            final = 0
            

        if oldLow > newLow:
            oldLow = newLow

    return [symbol, newHigh, newLow, oldHigh, oldLow, check, timee]

def dry_run_2(symbol, a, c):
    df = a.iloc[c:-1]
    up = 0
    newHigh = 0
    newLow = 0
    oldHigh = 0
    oldLow = 0
    check = 1
    final = 0
    highest = 0
    tempHigh = 0


    row = a.iloc[c:].iloc[0]
    final = 0
    lot = 0.02
    oldhighset = 1
    checkLow = 0
    finalLow = 0
    
    row = a.iloc[c:].iloc[0]
    if row.close > row.open:
        newHigh = row.close
        newLow = row.open
    else:
        newHigh = row.open
        newLow = row.close
        
    oldLow = 0
    oldHigh = newHigh
    print(oldHigh)
        
    #for a rising market
    for index, row in df.iterrows():
        print(index)
        print("close--{0:.5f}".format(row.close))
        print("open--{0:.5f}".format(row.open))
        print("newHigh--{0:.5f}".format(newHigh))
        print("newLow--{0:.5f}".format(newLow))
        print("oldHigh--{0:.5f}".format(oldHigh))
        print("oldLow--{0:.5f}".format(oldLow))
        print("tempHigh--{0:.5f}".format(tempHigh))

        # if row.close > newHigh and row.close < oldHigh:
        #     print("1")
        #     newHigh = row.close
        #     newLow = row.open

        if row.close > newHigh: #and row.close > oldHigh:
            print("1")
            newHigh = row.close
            newLow = row.open

            if oldhighset == 1:
                print("alpha")
                # oldLow = row.open #Set a counter here to wait for two up candles
                finalLow = 0
                checkLow = 1
                oldhighset = 0

        if row.close > oldHigh and row.close > row.open and check == 1:
            print("beta")
            if final == 1: #entering market after second candle consiqutively is up
                print(index, row.close, oldHigh)
                check = 0
                pass
            #Buy Signal

            final = final+1

        if row.close < newHigh and row.open > row.close:
            print("2")
            newLow = row.close
            newHigh = row.open
            if check == 0:
                print("3")
                oldHigh = newHigh
                oldhighset = 1
                timee = index
                check = 1  
            final = 0

            if row.close < oldLow:
                print("4")
                if finalLow == 0:
                    print("5")
                    tempHigh = row.open
                finalLow  = finalLow + 1


        if row.close > oldLow:
            print("6")
            checkLow = 0

        if check == 1 and finalLow == 2:
            print("7")
            oldHigh = tempHigh
            checkLow = 1 #indicator that SELL has to be executed
            print("Temp-->{}--{}".format(oldHigh, index))


        if checkLow == 1 and finalLow == 2:
            print("8")
            # finalLow = 0
            oldhighset = 1
            checkLow = 0
            #SELL call



        if row.close < newHigh and row.open < row.close:
            print("9")
            newLow = row.open
            newHigh = row.close
            oldLow = row.open #new

    return [symbol, newHigh, newLow, oldHigh, oldLow, check, timee]




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
 
def Profit_checker(ticket_no, symbol, signal, lot):
    print(ticket_no)
    count = 0
    while q == 0:
        try:
            order_status = mt5.positions_get(ticket=ticket_no)
            profit = order_status[0].profit
            rates_frame = get_values_1(symbol)
            if profit >= 1.0:
                Action_close(ticket_no, symbol, signal, lot)
                break
 
            elif profit <= -3.0:
                Action_close(ticket_no, symbol, signal, lot)
                break

        except Exception as e:
            print("Profit_checker")
            count = count+1
            if count>3:
                break
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

def run(var):
    try:
        symbol, newHigh, newLow, oldHigh, oldLow, check, timee = var
        final = 0
        lot = 0.02
        oldhighset = 0
        checkLow = 0
        finalLow = 0
        
        while True:
            row = get_values_1(symbol).iloc[-2]

            if row.close > newHigh:
                # if oldLow == 0:
                #     oldLow = newLow
                newHigh = row.close
                newLow = row.open

                if oldhighset == 1:
                    oldLow = row.open #Set a counter here to wait for two up candles
                    oldhighset = 0

            if row.close > oldHigh and row.close > row.open and check == 1:
                if final == 1: #entering market after second candle consiqutively is up
                    
                    q = 1 #Locks the meta trader for trading and prevents profit checker to send multiple requests

                    order_type = mt5.ORDER_TYPE_BUY
                    ask = row.close
                    bid = oldHigh
                    print(ask, bid)
                    buy_profit = price_action(symbol, lot, ask, bid, order_type)
                    print(buy_profit)
                    if buy_profit < 1.5:
                        signal = 1
                        result = Action(symbol, lot, signal)
                        check = 0 #keeps note of shot fired already i.e. trade taken already for that oldHigh
                        p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, lot))
                        p1.start()
                        # oldLow = 0
                    q = 0
                final = final+1

            # if row.close < newHigh and row.close < newLow:
            #     newLow = row.close
            #     newHigh = row.open  #Check and Final will be automatically set to zero only when the trades close, NOT HERE
                # if check == 0:
                #     oldHigh = newHigh
                #     check = 1
                # final = 0 

            elif row.close < newHigh and row.open > row.close:
                newLow = row.close
                newHigh = row.open
                if check == 0:
                    oldHigh = newHigh
                    oldhighset = 1
                    check = 1  
                final = 0

                if row.close < oldLow:
                    checkLow = 1
                    finalLow  = finalLow + 1


            elif row.close < newHigh and row.open < row.close:
                newLow = row.open
                newHigh = row.close

            if checkLow == 1 and final > 1: #ALSO Test for final = 0
                q = 1 #Locks the meta trader for trading and prevents profit checker to send multiple requests

                # order_type = mt5.ORDER_TYPE_SELL
                # ask = row.close
                # bid = oldLow
                # print(ask, bid)
                # buy_profit = price_action(symbol, lot, ask, bid, order_type)
                # print(buy_profit)
                # if buy_profit < 1.5:
                #     signal = 0
                #     result = Action(symbol, lot, signal)
                #     p1 = threading.Thread(target=Profit_checker, args=(result.order, symbol, signal, lot))
                #     p1.start()
                checkLow = 0
                q = 0



            # if oldLow > newLow:
            #     oldLow = newLow

            time.sleep(90)
    except Exception as e:
        print("run")
        print(e)


def manage(symbol):
    # a = get_values(symbol)
    # while True:
    #     if get_values(symbol).iloc[-2].close != a.iloc[-2].close:
    #         print("not equal start")
    #         break
    # try:

        a = get_values(symbol)
        c  = 1
        while True:
            if a.iloc[c].name == datetime(2021, 7, 1):
                break
            c+=1

        # var = dry_run(symbol,a, c)
        var = dry_run_2(symbol,a ,c)
        print(var)
        # run(var)
    # except Exception as e:
    #     print("Manage")
    #     print(e)

for symbol in ['GBPUSD']:#, 'USDJPY', 'CADJPY', 'EURUSD', 'EURGBP']:
    p2 = threading.Thread(target=manage, args=(symbol,))
    p2.start()
