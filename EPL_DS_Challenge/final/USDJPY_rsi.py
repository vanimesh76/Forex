#less negatives more positives

def get_values(symbol):
    timezone = pytz.timezone("Etc/UTC")
    x = datetime.now()
    utc_from = datetime(x.year, x.month, 19, tzinfo=timezone)    
    utc_to = datetime(x.year, x.month, x.day+1, tzinfo=timezone)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, utc_from, utc_to)

    rates_frame = pd.DataFrame(rates)
    rates_frame = rates_frame.drop(['tick_volume', 'spread', 'real_volume'], axis=1)
    # convert time in seconds into the datetime format
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame = rates_frame.set_index('time')
#     rates_frame['rsi'] = pta.rsi(rates_frame['close'], length = 14)
    
#     rates_frame['sma'] = rates_frame['close'].rolling(window=300).mean()
#     rates_frame['smaH'] = rates_frame['high'].rolling(window=30).mean()
#     rates_frame['smaL']= rates_frame['low'].rolling(window=20).mean()
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

symbol = "USDJPY"
a= get_values(symbol)
a['rsi'] = get_rsi(a['close'], 14)

B = []
check = 0
profit = []
index = []
indexB = []
counter = 0
peck = 0
p= []
checks = 0
counterr = 0
profits = []
up = 0
rsi1 = []
rsi2 = []
mul = 100000

for i in range(5, len(a)):
        if a.iloc[i-3].rsi < a.iloc[i-2].rsi and a.iloc[i-1].rsi < a.iloc[i-2].rsi \
            and a.iloc[i-1].rsi < a.iloc[i].rsi and a.iloc[i].rsi < a.iloc[i-2].rsi \
            and a.iloc[i].close > a.iloc[i].open \
            and (a.iloc[i].rsi - a.iloc[i-1].rsi) >= 2.0 \
             and check == 0:
#             and (a.iloc[i-2].rsi - a.iloc[i-3].rsi) >= 2.0
            
            buy_price = a.iloc[i+1].open
            print("#"*20)
            print(a.iloc[i+1].name)
            print("*"*20)
            check = 1  
            up = 0
            k = 0.0

        elif check == 1:
            sell_price = a.iloc[i].close
            pp = price_action(symbol, 1.0, buy_price, sell_price,mt5.ORDER_TYPE_SELL)
            print(f"{pp}---{round(a.iloc[i].rsi, 2)}---{a.iloc[i].close}--{a.iloc[i].name}")
            
            if pp >= 0.0:
                profit.append(pp)
                check = 0
            elif pp < 0.0:
                up = up+1
                if up > 1: 
                    profit.append(pp)
                    check = 0


                    #In live trade if loss still goes on to increase then close the trade before hand