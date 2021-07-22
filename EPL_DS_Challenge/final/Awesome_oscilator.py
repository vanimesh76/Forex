from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
import time
# import threading
mt5.initialize()

def price_action(symbol, lot, ask, bid, order_type):
    buy_profit=mt5.order_calc_profit(order_type,symbol,lot,ask,bid)
    return buy_profit
# price_action("EURUSD", 0.02, 1.17969, 1.18030,mt5.ORDER_TYPE_BUY)

def get_values(symbol):
    timezone = pytz.timezone("Etc/UTC")
    x = datetime.now()
    utc_from = datetime(2021, 2, 1, tzinfo=timezone)
    utc_to = datetime(x.year, x.month+1, x.day+1, tzinfo=timezone)
    # utc_to = datetime(x.year, x.month+1, 1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_H1, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop(['tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
    
    rates_frame['mean'] = (rates_frame['high'] + rates_frame['low'])/2

    # EMA = rates_frame['close'].ewm(span=100, adjust=False).mean()
    # DEMA = 2*EMA - EMA.ewm(span=100, adjust=False).mean()
    # rates_frame['dma'] = DEMA
    rates_frame['P34'] = rates_frame['mean'].rolling(window=34).mean()
    rates_frame['P5'] = rates_frame['mean'].rolling(window=5).mean()
#     rates_frame = rates_frame.fillna(0)
    rates_frame['AO'] = rates_frame['P5'] - rates_frame['P34']
    rates_frame = rates_frame.drop(['high', 'low', 'mean', 'P34', 'P5'], axis=1)
    return rates_frame

a = get_values("EURUSD")

l = ['NR']
for i in range(1,len(a)):
    df = a.iloc[i].AO
    dfo = a.iloc[i-1].AO
    if str(df) == 'nan':
        l.append('NR')
    else:
        if df <= 0.0:
            if df > dfo:
                l.append('NG')
            elif df < dfo:
                l.append("NR")
            else:
                print(type(df))
                l.append('R')
        elif df > 0.0:
            if df > dfo:
                l.append('PG')
            elif df < dfo:
                l.append("PR")
            else:
                print(type(df))
                l.append('NR')
        else:
            l.append('NR')
a['signal'] = l




B = []
check = 0
profit = []
index = []
indexB = 0
counter = 0
peck = 0
p= []
counterr = 0

for i in range(7, len(a)):
    df = a.iloc[i].signal
    dfo = a.iloc[i-1].signal
    if str(a.iloc[i].AO) != 'nan':
        if a.iloc[i].AO > -0.000500 and df == "NG" and check == 0:
            counter = 0
            for k in range(6,0, -1):
                if a.iloc[i-k].signal == "NG":
                    counter = counter + 1
                if a.iloc[i-k].signal == "NR":
                    break
        if counter == 6 and check == 0:
            B.append("buy")
            buy_price = a.iloc[i].close
            indexB = a.iloc[i].name
            print("#"*20)
            print(indexB)
            print("*"*20)
            
            check = 1
            counter = 0
        if check == 1:
            sell_price = a.iloc[i].close
            pp = price_action("EURUSD", 0.05, buy_price, sell_price, mt5.ORDER_TYPE_BUY)
            print(pp)
            if 'R' in df:
                print("R--{}".format(pp))
                check = 0
                index.append(a.iloc[i].name)
                print(a.iloc[i].name)
                profit.append([pp,indexB,a.iloc[i].name])
                p.append(pp)
            elif pp < -2.0:
                print("less--{}".format(pp))
                check = 0
                index.append(a.iloc[i].name)
                print(a.iloc[i].name)
                
                profit.append([pp,indexB,a.iloc[i].name])
                p.append(pp)
            else:
                counterr = 0
                index.append(0)
                B.append('nan')
#                 profit.append(0)


#     break
        
    
#     #860
#     a.iloc[i-2].AO == "PR" and a.iloc[i-2].AO == "PR" and a.iloc[i-2].AO > a.iloc[i-1].AO
#     #After ghad-bhad-2 NG PG goes up

# check for down also continuos red from PR to NR
#green aligator indicator crossing


sum(p)

profit