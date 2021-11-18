import MetaTrader5 as mt5
from pandas import DataFrame, to_datetime
import time

mt5.initialize()
global df


def get_values(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 20)

    rates_frame = DataFrame(rates)
    rates_frame['clsma']= rates_frame['close'].rolling(window=8).mean()
    rates_frame['smaC']= rates_frame['clsma'].rolling(window=8).mean()

    rates_frame['clsma']= rates_frame['open'].rolling(window=8).mean()
    rates_frame['smaO']= rates_frame['clsma'].rolling(window=8).mean()

    # rates_frame['time']=to_datetime(rates_frame['time'], unit='s')
    # rates_frame = rates_frame.set_index('time')
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

def run(symbol, df):
    lot = 0.02
    cl = df.iloc[-2].close+1
    op = df.iloc[-2].open+1
    check = 0
    checks = 0
    buy_up = 0
    sell_up = 0
    hour_passed = True
    buy = 1
    sell = 0

    print(symbol)            
    
    while True:
        if hour_passed:
            df = get_values(symbol)
            t = time.time()
            if df.iloc[-2].smaC < df.iloc[-2].smaO and check == 0:
                result_sell = Action(symbol, lot, sell)  #SELL Action
                if checks == 1 and buy_up == 0:
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment}")
                    if result_buy.comment == "Requote":
                        result_buy = Action_close(result_buy.order, symbol, buy, lot)
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment} ||| Requoted")

                    
                print(f"Symbol-->{symbol} ||| Type-->Sell ||| Ticket_No-->{result_sell.order} ||| result_comment-->{result_sell.comment}")
                sell_up = 0
                check = 1
                checks = 0

            if df.iloc[-2].smaC > df.iloc[-2].smaO and checks == 0:
                result_buy = Action(symbol, lot, buy)  #BUY Action

                if check == 1 and sell_up == 0:
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment}")
                    if result_sell.comment == "Requote":
                        result_sell = Action_close(result_sell.order, symbol, sell, lot)
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment} ||| Requoted")

                print(f"Symbol-->{symbol} ||| Type-->Buy ||| Ticket_No-->{result_buy.order} ||| result_comment-->{result_buy.comment}")
                buy_up = 0
                checks = 1
                check = 0
                
            cl = df.iloc[-2].close
            op = df.iloc[-2].open
            hour_passed = False


        ###############################################################
        
        if checks == 1 and buy_up == 0:
            sell_price = df.iloc[-1].close
            pp = mt5.positions_get(ticket=result_buy.order)[0].profit
            if pp > 1.0:
                result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close
                print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment}")
                if result_buy.comment == "Requote":
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment} ||| Requoted")
                buy_up = 1

        if check == 1 and sell_up == 0:
            sell_price = df.iloc[-1].close
            pp =mt5.positions_get(ticket=result_sell.order)[0].profit
            if pp >= 1.0:
                result_sell = Action_close(result_sell.order, symbol, sell, lot)
                print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment}")
                if result_sell.comment == "Requote":
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment} ||| Requoted")
                sell_up = 1


for symbol in ['EURGBP']:
    global df
    df = get_values(symbol)
    run(symbol,df)