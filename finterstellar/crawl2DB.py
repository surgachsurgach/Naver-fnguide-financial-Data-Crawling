import bs4
from urllib.request import urlopen
#import datetime as dt
import pandas as pd
import re
import json
import sqlite3

con = sqlite3.connect('db/fsdb01.db3')

class Price2DB:
      
    def get_daily_price_naver(self, cd, count):
        url = 'https://fchart.stock.naver.com/sise.nhn?symbol='+cd+'&timeframe=day&count='+str(count)+'&requestType=0'
        source = urlopen(url).read()
        soup = bs4.BeautifulSoup(source, 'lxml')
        prices = soup.find_all('item')

        daily = []
        for p in prices:
            data = p['data'].split('|')
            trade_date = pd.to_datetime(data[0]).date()
            price_open = float(data[1])
            price_high = float(data[2])
            price_low = float(data[3])
            price_close = float(data[4])
            trade_volume = int(data[5])
            daily.append([trade_date, price_open, price_high, price_low, price_close, trade_volume])

        df = pd.DataFrame(daily, columns=['trade_date', 'price_open', 'price_high', 'price_low', 'price_close', 'trade_volume'])
        df['Code'] = cd

        return(df)

    
    def make_query(self, df):
        query_string = ''
        for i in range(len(df)):
            # 시/고/저/종
            query = 'INSERT or REPLACE INTO price_daily (trade_date, code, price_open, price_high, price_low, price_close, trade_volume) VALUES ' 
            query = query + '("' + str(df.iloc[i, 0]) + '", '\
            + '"' + str(df.iloc[i, 6]) + '", '\
            + str(df.iloc[i, 1]) + ', '\
            + str(df.iloc[i, 2]) + ', '\
            + str(df.iloc[i, 3]) + ', '\
            + str(df.iloc[i, 4]) + ', '\
            + str(df.iloc[i, 5]) + '); ' 
            query_string = query_string + query
        return(query_string)
    
    
    def db_update(self, query_string):
        
        with con:
            cur = con.cursor()
            cur.executescript(query_string)
            
            
class DB2DF:
      
    def make_df(self, s_cd):
    
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd    
            
        price_df = pd.DataFrame()
        for cd in cds:
            tmp = dict()
            sql = 'SELECT trade_date, price_close FROM price_daily WHERE code=?'
            with con:
                cur = con.cursor()
                cur.execute(sql, [cd])
                rows = cur.fetchall()
                for r in rows:
                    tmp[r[0]] = r[1]
            sr = pd.Series(tmp)
            sr.name = cd
            price_df = pd.concat([price_df, sr], axis=1, sort=True)
            
        return(price_df)