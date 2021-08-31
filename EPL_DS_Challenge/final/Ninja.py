import MetaTrader5 as mt5
from pandas import DataFrame, to_datetime
import time
import pytz
from datetime import datetime

mt5.initialize()
global df


def get_values(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)

    rates_frame = DataFrame(rates)
    
    rates_frame['time']= to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
    rates_frame = rates_frame.drop(['tick_volume', 'spread', 'real_volume',], axis=1)
    v = niss_Fast(rates_frame['close'])
    rates_frame['nissFast'] = [0]*(len(rates_frame['close']) - len(v)) + v
    v = niss_Slow(rates_frame['close'])
    rates_frame['nissSlow'] = [0]*(len(rates_frame['close']) - len(v)) + v
    
    rates_frame['nissOscRaw'] = [0]*69 + list(map(lambda x,y : ((x - y)/y)*100, rates_frame['nissFast'][69:], rates_frame['nissSlow'][69:]))

    rates_frame['nissOsc'] = rates_frame['nissOscRaw'].rolling(window=1).mean()
    
    v = ema(rates_frame['nissOscRaw'], 24)
    rates_frame['nissSignal'] = [0]*(len(rates_frame['close']) - len(v)) + v
    

    return rates_frame

def ema(s, n):
    ema = []
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema

def niss_Fast(src):
    emaF1 = ema(src, 3)
    emaF2 = ema(src, 5)
    emaF3 = ema(src, 7)
    emaF4 = ema(src, 9)
    emaF5 = ema(src, 11)
    emaF6 = ema(src, 13)
    emaF7 = ema(src, 15)
    emaF8 = ema(src, 17)
    emaF9 = ema(src, 19)
    emaF10 = ema(src, 21)
    emaF11 = ema(src, 23)
    return list(map(lambda x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11:(x1+x2+x3+x4+x5+x6+x7+x8+x9+x10+x11)/11, \
             emaF1[len(emaF1)-len(emaF11):], \
             emaF2[len(emaF2)-len(emaF11):],  emaF3[len(emaF3)-len(emaF11):], emaF4[len(emaF4)-len(emaF11):], \
            emaF5[len(emaF5)-len(emaF11):], emaF6[len(emaF6)-len(emaF11):], emaF7[len(emaF7)-len(emaF11):], \
            emaF8[len(emaF8)-len(emaF11):], emaF9[len(emaF9)-len(emaF11):], emaF10[len(emaF10)-len(emaF11):], \
            emaF11))
    
def niss_Slow(src):
    emaS1 = ema(src, 25)
    emaS2 = ema(src, 28)
    emaS3 = ema(src, 31)
    emaS4 = ema(src, 34)
    emaS5 = ema(src, 37)
    emaS6 = ema(src, 40)
    emaS7 = ema(src, 43)
    emaS8 = ema(src, 46)
    emaS9 = ema(src, 49)
    emaS10 = ema(src, 52)
    emaS11 = ema(src, 55)
    emaS12 = ema(src, 58)
    emaS13 = ema(src, 61)
    emaS14 = ema(src, 64)
    emaS15 = ema(src, 67)
    emaS16 = ema(src, 70)
    return list(map(lambda x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16: \
                    (x1+x2+x3+x4+x5+x6+x7+x8+x9+x10+x11+x12+x13+x14+x15+x16)/16, \
         emaS1[len(emaS1)-len(emaS16):], \
         emaS2[len(emaS2)-len(emaS16):],  emaS3[len(emaS3)-len(emaS16):], emaS4[len(emaS4)-len(emaS16):], \
        emaS5[len(emaS5)-len(emaS16):], emaS6[len(emaS6)-len(emaS16):], emaS7[len(emaS7)-len(emaS16):], \
        emaS8[len(emaS8)-len(emaS16):], emaS9[len(emaS9)-len(emaS16):], emaS10[len(emaS10)-len(emaS16):], \
        emaS11[len(emaS11)-len(emaS16):], emaS12[len(emaS12)-len(emaS16):], emaS13[len(emaS13)-len(emaS16):], \
                   emaS14[len(emaS14)-len(emaS16):], emaS15[len(emaS15)-len(emaS16):], emaS16))

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

    buy = 1
    sell = 0

    print(symbol)

    while True:
        df = get_values(symbol)
        if df.iloc[-2].nissOsc < df.iloc[-2].nissSignal and df.iloc[-3].nissOsc >= df.iloc[-3].nissSignal:
            hour_passed = True
            break

        elif df.iloc[-2].nissOsc > df.iloc[-2].nissSignal and df.iloc[-3].nissOsc <= df.iloc[-3].nissSignal:
            hour_passed = True
            break

        t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
        print(f"SLeep Time-->{((60*60 - t.minute*60) + 5)}")
        time.sleep((60*60 - t.minute*60) + 5)


    while True:
        if hour_passed:
            df = get_values(symbol)
            if df.iloc[-2].nissOsc < df.iloc[-2].nissSignal and sell_check == 0:
                result_sell = Action(symbol, lot, sell)

                if buy_up == 1:
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                    if result_buy.comment == "Requote":
                        result_buy = Action_close(result_buy.order, symbol, buy, lot)
                        print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment}")
                    buy_up = 0


                print(f"Symbol-->{symbol} ||| Ticket_No-->{result_sell.order}")
                sell_up = 1
                sell_check = 1
                buy_check = 0

            if df.iloc[-2].nissOsc > df.iloc[-2].nissSignal and buy_check == 0:
                result_buy = Action(symbol, lot, buy)
                
                if sell_up == 1:
                    result_sell = Action_close(result_sell.order, symbol, sell, lot)   #Action_close
                    
                    if result_sell.comment == "Requote":
                        result_sell = Action_close(result_sell.order, symbol, sell, lot)
                        print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment} ||| Requoted")
                    else:
                        print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment}")
                    sell_up = 0

                print(f"Symbol-->{symbol} ||| Type-->Buy ||| Ticket_No-->{result_buy.order} ||| result_comment-->{result_buy.comment}")
                buy_up = 1
                buy_check = 1
                sell_check = 0

            hour_passed = False
            print(f"hour_passed--->{hour_passed}")

            #############################################################

        if buy_check == 1 and buy_up == 1:
            pp = mt5.positions_get(ticket=result_buy.order)[0].profit
            if pp > 1.0:
                result_buy = Action_close(result_buy.order, symbol, buy, lot)     #Action_close

                if result_buy.comment == "Requote":
                    result_buy = Action_close(result_buy.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| Type-->Buy ||| result_comment-->{result_buy.comment}")
                buy_up = 0

        if sell_check == 1 and sell_up == 1:
            pp = mt5.positions_get(ticket=result_sell.order)[0].profit
            if pp > 1.0:
                result_sell = Action_close(result_sell.order, symbol, buy, lot)     #Action_close

                if result_sell.comment == "Requote":
                    result_sell = Action_close(result_sell.order, symbol, buy, lot)
                    print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment} ||| Requoted")
                else:
                    print(f"Close  Symbol-->{symbol} ||| Type-->Sell ||| result_comment-->{result_sell.comment}")
                sell_up = 0

        if buy_check == 1 and buy_up == 0:
            t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
            print(f"SLeep Time-->{((60*60 - t.minute*60) + 5)}")
            time.sleep((60*60 - t.minute*60) + 5)
            hour_passed = True

        if sell_check == 1 and sell_up == 0:
            t = datetime.fromtimestamp(time.time(), tz= pytz.timezone('Etc/GMT-3'))
            print(f"SLeep Time-->{((60*60 - t.minute*60) + 5)}")
            time.sleep((60*60 - t.minute*60) + 5)
            hour_passed = True

for symbol in ['EURGBP']:
    run(symbol)