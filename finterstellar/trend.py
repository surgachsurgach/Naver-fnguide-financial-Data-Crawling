import pandas as pd


class Trend():
    
    def MA(self, df, cd, long, short, base_date):
        ma = pd.DataFrame()
        ma[cd] = df[cd].copy()
        ma['MA'+str(long)] = df[cd].rolling(long).mean()
        ma['MA'+str(short)] = df[cd].rolling(short).mean()
        return (ma[base_date:])
    
    
    def RSI(self, df, cd, period, base_date):
        rsi_df = pd.DataFrame()
        rsi_df[cd] = df[cd].copy()
        rsi_df = rsi_df.dropna()
        rsi_df['diff'] = rsi_df[cd] - rsi_df[cd].shift(1)
        for p in rsi_df.iloc[period:].index:
            d, ad, u, au = 0, 0., 0, 0.
            for i in range(period):
                diff = rsi_df.shift(i).loc[p, 'diff']
                if diff >= 0:
                    u += 1
                    au += diff
                elif diff < 0:
                    d += 1
                    ad -= diff
            if not au + ad == 0:
                rsi = round (au / (au + ad), 4) * 100
            else:
                rsi = 0
            rsi_df.loc[p, 'RSI'+str(period)] = rsi
        return (rsi_df[base_date:])
    
    
    def WRSI(self, df, cd, period, base_date):
        rsi_df = pd.DataFrame()
        rsi_df[cd] = df[cd].copy()
        rsi_df = rsi_df.dropna()
        rsi_df['diff'] = rsi_df[cd] - rsi_df[cd].shift(1)
        for p in rsi_df.iloc[period:].index:
            d, ad, u, au, multiple = 0, 0., 0, 0., 0.
            for i in range(period):
                multiple = (period - i) / period
                diff = rsi_df.shift(i).loc[p, 'diff']
                if diff >= 0:
                    u += 1
                    au += diff * multiple
                elif diff < 0:
                    d += 1
                    ad -= diff * multiple
            if not au + ad == 0:
                rsi = round (au / (au + ad), 4) * 100
            else:
                rsi = 0
            rsi_df.loc[p, 'WRSI'+str(period)] = rsi
        return (rsi_df[base_date:])
