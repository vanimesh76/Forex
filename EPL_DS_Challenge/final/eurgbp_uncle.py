import MetaTrader5 as mt5
from pandas import DataFrame, to_datetime
import time
import pytz
from datetime import datetime

mt5.initialize()
global df


def get_values(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 30)

    rates_frame = DataFrame(rates)
    rates_frame['clsma']= rates_frame['close'].rolling(window=8).mean()
    rates_frame['smaC']= rates_frame['clsma'].rolling(window=8).mean()

    rates_frame['clsma']= rates_frame['open'].rolling(window=8).mean()
    rates_frame['smaO']= rates_frame['clsma'].rolling(window=8).mean()

    rates_frame['time']=to_datetime(rates_frame['time'], unit='s')
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
    lot = 0.02
    check = 0
    buy_check = 0
    sell_check = 0
    buy_up = 0
    sell_up = 0

    buy = 1
    sell = 0

    while True:
        df = get_values(symbol)
        if df.iloc[-2].smaC < df.iloc[-2].smaO and df.iloc[-3].smaC >= df.iloc[-3].smaO:
            hour_passed = True
            break

        elif df.iloc[-2].smaC > df.iloc[-2].smaO and df.iloc[-3].smaC <= df.iloc[-3].smaO:
            hour_passed = True
            break

        t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
        print(f"SLeep Time-->{((60*60 - t.minute*60) + 5)}")
        time.sleep((60*60 - t.minute*60) + 5)


    print(symbol)            
    
    while True:
        if hour_passed:
            df = get_values(symbol)
            if df.iloc[-2].smaC < df.iloc[-2].smaO and sell_check == 0:
                result_sell = Action(symbol, lot, sell)  #SELL Action

                if buy_check == 1 and buy_up == 0:
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                    if result_buy.comment == "Requote":
                        result_buy = Action_close(result_buy.order, symbol, buy, lot)
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment}")

                print(f"Symbol-->{symbol} ||| Type-->Sell ||| Ticket_No-->{result_sell.order} ||| result_comment-->{result_sell.comment}")
                sell_up = 0
                sell_check = 1

                buy_check = 0
                order_time = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3')).hour

            if df.iloc[-2].smaC > df.iloc[-2].smaO and buy_check == 0:
                result_buy = Action(symbol, lot, buy)  #BUY Action

                if sell_check == 1 and sell_up == 0:
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment}")
                    if result_sell.comment == "Requote":
                        result_sell = Action_close(result_sell.order, symbol, sell, lot)
                        print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment} ||| Requoted")

                print(f"Symbol-->{symbol} ||| Type-->Buy ||| Ticket_No-->{result_buy.order} ||| result_comment-->{result_buy.comment}")
                buy_up = 0
                buy_check = 1

                sell_check = 0
                order_time = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3')).hour

            hour_passed = False


        ###############################################################
        
        if buy_check == 1 and buy_up == 0:
            pp = mt5.positions_get(ticket=result_buy.order)[0]

            if pp.profit > 1.0:
                result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                if result_buy.comment == "Requote":
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_buy.comment}")
                buy_up = 1

        if sell_check == 1 and sell_up == 0:
            pp = mt5.positions_get(ticket=result_sell.order)[0]

            if pp.profit >= 1.0:
                result_sell = Action_close(result_sell.order, symbol, sell, lot)

                if result_sell.comment == "Requote":
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| result_comment-->{result_sell.comment}")
                sell_up = 1


        t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
        if buy_check == 1 and buy_up == 1:
            print(f"SLeep Time-->{((60*60 - t.minute*60) + 5)}")
            time.sleep((60*60 - t.minute*60) + 5)
            hour_passed = True

        if sell_check == 1 and sell_up == 1:
            print(f"SLeep Time-->{((60*60 - t.minute*60) + 5)}")
            time.sleep((60*60 - t.minute*60) + 5)
            hour_passed = True

        if order_time != t.hour:
            order_time = t.hour
            hour_passed = True

for symbol in ['EURUSD']:
    # run(symbol)

    df = get_values(symbol)
    for i in range(15, len(df)):
        df = get_values(symbol)
        if df.iloc[i].smaC < df.iloc[i].smaO and df.iloc[i-1].smaC >= df.iloc[i-1].smaO:
            print("fdfdf")
            print(df.iloc[i].name)
            hour_passed = True
            # break

        elif df.iloc[i].smaC > df.iloc[i].smaO and df.iloc[i-1].smaC <= df.iloc[i-1].smaO:
            print("gfgf")
            print(df.iloc[i].name)
            hour_passed = True
            # break


##########################
'''Intervene RSI 14 period'''
############################




#EURGBP
#When reaching up wait for the AO to turn red when RSI above 60 and wait for Either RSI to fall below 60 or AO to turn RED for 
#enough candles Initiate Sell Signal

#BUY_Signal when RSI crosses Above 40 mark wait for it to reach 60


#Trust the 1-Hour short if 1 Day Uncle signal is Red
#And Trust Long if 1 Day signal is Green

#datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))