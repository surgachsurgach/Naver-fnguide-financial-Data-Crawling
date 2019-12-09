import pandas as pd
import numpy as np
import datetime as dt
from .common import CommonFunctions as cfs
    

class LoadData:

    
    def read_investing_price(self, path, cd):
        file_name = path + cd + ' Historical Data.csv'
        df = pd.read_csv(file_name, index_col='Date')
        return (df)
    

    def create_portfolio_df(self, path, p_name, p_cd):
        new_df = self.make_historical_price_df(path, p_cd) 
        prices_df = self.create_master_file(path, p_name, new_df)
        prices_df = self.update_master_file(path, p_name, new_df)
        return (prices_df)

    
    def make_historical_price_df(self, path, s_cd):
        cds = cfs.str_list(s_cd)
        dates = pd.Series()
        for c in cds:
            prices_df = self.read_investing_price(path, c)
            prices_df = self.date_formatting(prices_df)
            c = prices_df['Price']
            dates_new = pd.Series(prices_df.index)
            dates = dates.append(dates_new)
        dates = dates.drop_duplicates().sort_values().reset_index()
        dates = dates.drop(['index'], axis=1)
        universe_df = pd.DataFrame(index=dates[0])
        universe_df.index.name = 'Date'
        for c in cds:
            prices_df = self.read_investing_price(path, c)
            prices_df = self.date_formatting(prices_df)
            prices_df = self.price_df_trimming(prices_df, c)
            universe_df[c] = prices_df[c]
        universe_df
        universe_df = universe_df.fillna(method='ffill')
        return (universe_df)
    

    
    def create_master_file(self, path, f_name, df):
        file_name = path + 'fs ' + f_name + '.csv'
        try:
            f = open(file_name)
            print('Updating master file')
            f.close()
        except IOError as e:
            df.index = pd.to_datetime(df.index)
            df.index.name = 'Date'
            #df = df.fillna(method='ffill')
            #today_date = pd.Timestamp.today().date().strftime('%y%m%d')
            df.to_csv(file_name)
        return (df)    
    
    
    def update_master_file(self, path, n, new_df):
        try:
            file_name = 'fs ' + n + '.csv'
            master_df = self.read_master_file(path, n)
            universe_df = new_df.combine_first(master_df)
            universe_df.index.name = 'Date'
            #universe_df = universe_df.fillna(method='ffill')
            universe_df.to_csv(path + file_name)
        except IOError as e:
            print('Creating master file')
            self.create_master_file(path, n, new_df)
            universe_df = new_df
        return (universe_df)
    
    

    def read_master_file(self, path, n):
        file_name = path + 'fs ' + n + '.csv'
        prices_df = pd.read_csv(file_name, index_col='Date')
        dates = []     
        for i in prices_df.index:
            d = pd.to_datetime(i)
            dates.append(d)
        prices_df['Date'] = dates     # Date 값 교체
        prices_df = prices_df.set_index('Date')
        return (prices_df)
    
    def get_codes(self, prices_df):
        codes = prices_df.columns.values
        return (codes)


    def read_raw_csv(self, path, n):
        file_name = path + n + '.csv'
        df = pd.read_csv(file_name, index_col='Date')
        dates = []     
        for i in df.index:
            #d = dt.datetime.strptime(i, '%Y-%m-%d')
            d = pd.to_datetime(i)
            dates.append(d)
        df['Date'] = dates     # Date 값 교체
        df = df.set_index('Date')
        df.sort_index(axis=0, inplace=True)
        return (df)


    def read_raw_excel(self, path, n, sheet=None):
        file_name = path + n
        df = pd.read_excel(file_name, index_col=0)
        dates = []     
        for i in df.index:
            d = pd.to_datetime(i)
            dates.append(d)
        df['Date'] = dates     # Date 값 교체
        df = df.set_index('Date')
        df.sort_index(axis=0, inplace=True)
        return (df)
    
    
    def date_formatting(self, df):
        dates = []     
        for i in df.index:
            #d = dt.datetime.strptime(df.iloc[i,0], '%b %d, %Y')
            #d = pd.to_datetime(df.iloc[i,0])
            d = pd.to_datetime(i)
            dates.append(d)
        df['Date'] = dates     # Date 값 교체
        df = df.set_index('Date')
        #df = df.sort_index()
        return (df)
    
    
    def price_formatting(self, df, c='Price'):
        for i in df.index:
            p = df.loc[i, c]
            try:
                p = p.replace(',', '')
            except:
                pass
            df.loc[i, c] = float(p)
        return (df)
    
    
    def price_df_trimming(self, df, cd):
        prices = []
        for i in df.index:
            p = df['Price'].loc[i]
            try:
                p = p.replace(',', '')
            except:
                pass
            prices.append(float(p))
        df[cd] = prices
        df_new = pd.DataFrame(df[cd])
        #df = df.drop(df.columns[1:], axis=1)
        df_new = df_new.sort_index()
        return (df_new)
    
    
    def read_intraday_csv(self, path, n):
        file_name = path + n + '.csv'
        df = pd.read_csv(file_name, index_col=0)
        time = []     
        for i in df.index:
            d = pd.to_datetime(i).time()
            time.append(d)
        df['Time'] = time     # Date 값 교체
        df = df.set_index('Time')
        df.sort_index(axis=0, inplace=True)
        return (df)

    
    def read_intraday_excel(self, path, n):
        file_name = path + n + '.xlsx'
        df = pd.read_excel(file_name, index_col=0)
        time = []     
        for i in df.index:
            d = pd.to_datetime(i).time()
            time.append(d)
        df['Time'] = time     # Date 값 교체
        df = df.set_index('Time')
        df.sort_index(axis=0, inplace=True)
        return (df)

