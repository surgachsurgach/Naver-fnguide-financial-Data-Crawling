'''
    intraday trading module
'''    
import pandas as pd
import numpy as np
import datetime as dt


class IntradayTrade:
    
    def sampling(self, prices_df, s_date, s_codes):
        sample = pd.DataFrame()
        sample = prices_df.loc[s_date:][s_codes].copy()
        return (sample)
    
    def create_trade_book(self, sample, s_cd):
        book = pd.DataFrame()
        book[s_cd] = sample[s_cd]
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
        for c in cds:
            book['t '+c] = ''
            book['p '+c] = ''
        return (book) 
  
    
    def position(self, book, s_cd):
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
        for c in cds:
            status = ''
            for i in book.index:
                if book.loc[i, 't '+c] == 'buy':
                    if book.shift(1).loc[i, 't '+c] == 'buy':
                        status = 'll'
                    elif book.shift(1).loc[i, 't '+c] == '':
                        status = 'zl'
                    elif book.shift(1).loc[i, 't '+c] == 'sell':
                        status = 'sl'
                    else:
                        status = 'zl'
                elif book.loc[i, 't '+c] == 'sell':
                    if book.shift(1).loc[i, 't '+c] == 'buy':
                        status = 'ls'
                    elif book.shift(1).loc[i, 't '+c] == '':
                        status = 'zs'
                    elif book.shift(1).loc[i, 't '+c] == 'sell':
                        status = 'ss'
                    else:
                        status = 'zs'
                elif book.loc[i, 't '+c] == '':
                    if book.shift(1).loc[i, 't '+c] == 'buy':
                        status = 'lz'
                    elif book.shift(1).loc[i, 't '+c] == '':
                        status = 'zz'
                    elif book.shift(1).loc[i, 't '+c] == 'sell':
                        status = 'sz'
                    else:
                        status = 'zz'
                else:
                    status = 'zz'
                book.loc[i, 'p '+c] = status
        return (book)
      
   

    def position_strategy(self, book, s_cd, last_date):
        
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
        
        strategy = ''
        for c in cds:
            i = book.index[-1]
            if book.loc[i, 'p '+c] == 'lz' or book.loc[i, 'p '+c] == 'sz' or book.loc[i, 'p '+c] == 'zz':
                strategy = 'nothing'
            elif book.loc[i, 'p '+c] == 'll' or book.loc[i, 'p '+c] == 'sl' or book.loc[i, 'p '+c] == 'zl':
                strategy += 'long '+c
            elif book.loc[i, 'p '+c] == 'ls' or book.loc[i, 'p '+c] == 'ss' or book.loc[i, 'p '+c] == 'zs':
                strategy += 'short '+c
        print ('As of', last_date, 'your model portfolio', cds,'needs to be composed of', strategy)
        return (strategy)


 
    
    def returns(self, book, s_cd, display=False):
        # 손익 계산
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd

        rtn = 1.0
        book['return'] = 1
        for c in cds:
            buy = 0.0
            sell = 0.0
            for i in book.index:
            
                if book.loc[i, 'p '+c] == 'zl' or book.loc[i, 'p '+c] == 'sl' :     # long 진입
                    buy = book.loc[i, c]
                    if display == True:
                        print(i, 'long '+c, buy)
                elif book.loc[i, 'p '+c] == 'lz' or book.loc[i, 'p '+c] == 'ls' :     # long 청산
                    sell = book.loc[i, c]
                    # 손익 계산
                    rtn = (sell - buy) / buy + 1
                    book.loc[i, 'return'] = rtn
                    if display == True:
                        print(i, 'long '+c, buy, ' | unwind long '+c, sell, ' | return:', round(rtn, 4))
                    
                elif book.loc[i, 'p '+c] == 'zs' or book.loc[i, 'p '+c] == 'ls' :     # short 진입
                    sell = book.loc[i, c]
                    if display == True:
                        print(i, 'short '+c, sell)
                elif book.loc[i, 'p '+c] == 'sz' or book.loc[i, 'p '+c] == 'sl' :     # short 청산
                    buy = book.loc[i, c]
                    # 손익 계산
                    rtn = (sell - buy) / sell + 1
                    book.loc[i, 'return'] = rtn
                    if display == True:
                        print(i, 'short '+c, sell, ' | unwind short '+c, buy, ' | return:', round(rtn, 4))
                
            if book.loc[i, 't '+c] == '' and book.loc[i, 'p '+c] == '':     # zero position
                buy = 0.0
                sell = 0.0
        
        acc_rtn = 1.0
        for i in book.index:
            rtn = book.loc[i, 'return']
            acc_rtn = acc_rtn * rtn
            book.loc[i, 'acc return'] = acc_rtn
            
        print ('Accunulated return :', round(acc_rtn, 2), '%')
        return (round(acc_rtn, 4))

           
   
    def benchmark_return(self, book, s_cd):
        # 벤치마크 수익률
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        n = len(cds)
        rtn = dict()
        acc_rtn = float()
        for c in cds:
            rtn[c] = round (( book[c].iloc[-1] - book[c].iloc[0] ) / book[c].iloc[0] + 1, 4)
            acc_rtn += rtn[c]/n
        print('BM return:', round(acc_rtn, 2), '%')
        print(rtn)
        return (round(acc_rtn, 4))
    
        
    def excess_return(self, fund_rtn, bm_rtn):
        exs_rtn = fund_rtn - bm_rtn
        print('Excess return:', round(exs_rtn, 2), '%')
        return (exs_rtn)


    def returns_log(self, book, s_cd, display=False):
        # 손익 계산
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        rtn = 0.0
        book['return'] = rtn
        
        for c in cds:
            buy = 0.0
            sell = 0.0
            for i in book.index:
            
                if book.loc[i, 'p '+c] == 'zl' or book.loc[i, 'p '+c] == 'sl' :     # long 진입
                    buy = book.loc[i, c]
                    if display == True:
                        print(i.date(), 'long '+c, buy)
                elif book.loc[i, 'p '+c] == 'lz' or book.loc[i, 'p '+c] == 'ls' :     # long 청산
                    sell = book.loc[i, c]
                    # 손익 계산
                    rtn = np.log(sell / buy) * 100
                    #(sell - buy) / buy + 1
                    book.loc[i, 'return'] = rtn
                    if display == True:
                        print(i.date(), 'long '+c, buy, ' | unwind long '+c, sell, ' | return:', round(rtn, 4))
                    
                elif book.loc[i, 'p '+c] == 'zs' or book.loc[i, 'p '+c] == 'ls' :     # short 진입
                    sell = book.loc[i, c]
                    if display == True:
                        print(i.date(), 'short '+c, sell)
                elif book.loc[i, 'p '+c] == 'sz' or book.loc[i, 'p '+c] == 'sl' :     # short 청산
                    buy = book.loc[i, c]
                    # 손익 계산
                    rtn = np.log(sell / buy) * 100
                    book.loc[i, 'return'] = rtn
                    if display == True:
                        print(i.date(), 'short '+c, sell, ' | unwind short '+c, buy, ' | return:', round(rtn, 4))
                
            if book.loc[i, 't '+c] == '' and book.loc[i, 'p '+c] == '':     # zero position
                buy = 0.0
                sell = 0.0
        
        acc_rtn = 0.0
        for i in book.index:
            rtn = book.loc[i, 'return']
            acc_rtn = acc_rtn + rtn
            book.loc[i, 'acc return'] = acc_rtn
            
        print ('Accunulated return :', round((acc_rtn - 1) * 100, 2), '%')
        return (round(acc_rtn, 4))

    
   
    def benchmark_return_log(self, book, s_cd):
        # 벤치마크 수익률
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        n = len(cds)
        rtn = dict()
        acc_rtn = float()
        for c in cds:
            rtn[c] = round ( np.log(book[c].iloc[-1] / book[c].iloc[0]) * 100 , 4)   
            acc_rtn += rtn[c]/n
        print('BM return:', round((acc_rtn - 1) * 100, 2), '%')
        print(rtn)
        return (round(acc_rtn, 4))
    
        
    def excess_return_log(self, fund_rtn, bm_rtn):
        exs_rtn = np.log(fund_rtn / bm_rtn) * 100
        print('Excess return:', round(exs_rtn, 2), '%')
        return (exs_rtn)    
    
    
    
class IntradayFuturesTradeOnValue(IntradayTrade):
    
    
    def expected_y(self, sample, s_codes, r, d, t, T):
        from finterstellar import Valuation
        vu = Valuation()
        for i in sample.index:
            sample.loc[i, s_codes[1]+' expected'] = vu.futures_price(sample.loc[i, s_codes[0]], r, d, t, T)
        sample[s_codes[1]+' spread'] = sample[s_codes[1]] - sample[s_codes[1]+' expected']
        return (sample)

    
    
    def price_analyze(self, sample, thd, s_codes):
        for i in sample.index:
            threshold = float( thd * sample.loc[i, s_codes[1]] )
            if sample.loc[i, s_codes[1]+' spread'] > 0:
                sample.loc[i, 'cheaper'] = s_codes[0]
            elif sample.loc[i, s_codes[1]+' spread'] < -threshold:
                sample.loc[i, 'cheaper'] = s_codes[1]
            else:
                sample.loc[i, 'cheaper'] = 'E'
        print(sample.groupby('cheaper').count())
        return (sample)    
      
    
    def tradings(self, sample, book, thd, s_codes):
        for i in sample.index:
            threshold = float( thd * sample.loc[i, s_codes[1]] )
            if sample.loc[i, s_codes[1]+' spread'] > threshold:
                book.loc[i, 't '+s_codes[1]] = 'sell'
            elif threshold >= sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= 0:
                book.loc[i, 't '+s_codes[1]] = 'sell'
            elif 0 > sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= -threshold:
                book.loc[i, 't '+s_codes[1]] = ''
            elif -threshold > sample.loc[i, s_codes[1]+' spread']:
                book.loc[i, 't '+s_codes[1]] = 'buy'
        return (book) 
    


    def trading_strategy(self, sample, thd, s_codes, last_date):
        i = sample.index[-1]
        threshold = float( thd * sample.loc[i, s_codes[1]] )
        
        if sample.loc[i, s_codes[1]+' spread'] > threshold:
            strategy = 'sell '+s_codes[1]
        elif threshold >= sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= 0:
            strategy = 'sell '+s_codes[1]
        elif 0 > sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= -threshold:
            strategy = 'do nothing'
        elif -threshold > sample.loc[i, s_codes[1]+' spread']:
            strategy = 'buy '+s_codes[1]

        print ('As of', last_date, 'this model suggests you to', strategy)
        return (strategy) 
    

        
class IntradayFuturesTradeOnBasis(IntradayTrade):
    
    def basis_calculate(self, df, pair):
        basis = df[pair[1]] - df[pair[0]]
        df['basis'] = basis
        return (df)
    
    
    def price_analyze(self, sample, thd, s_codes):
        for i in sample.index:
            if sample.loc[i, 'basis'] > thd:
                sample.loc[i, 'cheaper'] = s_codes[0]
            elif sample.loc[i, 'basis'] < 0:
                sample.loc[i, 'cheaper'] = s_codes[1]
            else:
                sample.loc[i, 'cheaper'] = 'E'
        print(sample.groupby('cheaper').count())
        return (sample)
    
    
    def tradings(self, sample, book, thd, s_codes):
        for i in sample.index:
            if sample.loc[i, 'basis'] > thd:
                book.loc[i, 't '+s_codes[1]] = 'sell'
            elif thd >= sample.loc[i, 'basis'] and sample.loc[i, 'basis'] >= 0:
                book.loc[i, 't'+s_codes[1]] = ''
            elif 0 > sample.loc[i, 'basis']:
                book.loc[i, 't '+s_codes[1]] = 'buy'
        return (book) 
    
    
    def trading_strategy(self, sample, thd, s_codes, last_date):
        i = sample.index[-1]
        
        if sample.loc[i, 'basis'] > thd:
            strategy = 'sell '+s_codes[1]
        elif thd >= sample.loc[i, 'basis'] and sample.loc[i, 'basis'] >= 0:
            strategy = 'do nothing'
        elif 0 > sample.loc[i, 'basis']:
            strategy = 'buy '+s_codes[1]
  
        print ('As of', last_date, 'this model suggests you to', strategy)
        return (strategy) 
    
    
class IntradayBBTrade(IntradayTrade):
    
    def bollinger_band(self, prices_df, s_cd, n, sigma):
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        bb = pd.DataFrame()
        bb[cds[0]] = prices_df[cds[0]]
        bb['center'] = prices_df[cds[0]].rolling(n).mean()
        bb['ub'] = bb['center'] + sigma * prices_df[cds[0]].rolling(n).std()
        bb['lb'] = bb['center'] - sigma * prices_df[cds[0]].rolling(n).std()
        return (bb)
    
    
    def tradings(self, sample, book, thd, s_cd, buy='in', short=False):
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        for i in sample.index:
            price = sample.loc[i, cds[0]]
            
            if short == True:
                
                if price > sample.loc[i, 'ub']:
                    if book.shift(1).loc[i, 't '+cds[0]] == 'sell':    # 이미 매수상태라면
                        book.loc[i, 't '+cds[0]] = 'sell'     # 매수상태 유지
                    else:
                        if buy == 'in':   # 밴드 진입 시 매수
                            book.loc[i, 't '+cds[0]] = 'ready'    # 대기
                        else:
                            book.loc[i, 't '+cds[0]] = 'sell'     # 매수

                elif sample.loc[i, 'ub'] >= price and price > sample.loc[i, 'center']:
                    if buy == 'out':
                        if book.shift(1).loc[i, 't '+cds[0]] == 'sell':     # 숏 유지
                            book.loc[i, 't '+cds[0]] = 'sell'
                        elif book.shift(1).loc[i, 't '+cds[0]] == 'buy':    # 롱 청산
                            book.loc[i, 't '+cds[0]] = ''  
                        else:
                            book.loc[i, 't '+cds[0]] = ''  
                    else:
                        if book.shift(1).loc[i, 't '+cds[0]] == 'sell' or book.shift(1).loc[i, 't '+cds[0]] == 'ready': 
                            book.loc[i, 't '+cds[0]] = 'sell'
                        elif book.shift(1).loc[i, 't '+cds[0]] == 'buy':    # 롱 청산
                            book.loc[i, 't '+cds[0]] = ''  
                        else:
                            book.loc[i, 't '+cds[0]] = ''  
                            
                elif sample.loc[i, 'center'] >= price and price > sample.loc[i, 'lb']:
                    if buy == 'out':
                        if book.shift(1).loc[i, 't '+cds[0]] == 'sell':    # 숏 청산
                            book.loc[i, 't '+cds[0]] = ''
                        elif book.shift(1).loc[i, 't '+cds[0]] == 'buy':    # 롱 유지
                            book.loc[i, 't '+cds[0]] = 'buy'  
                        else:
                            book.loc[i, 't '+cds[0]] = ''  
                    else:
                        if book.shift(1).loc[i, 't '+cds[0]] == 'sell':    # 숏 청산
                            book.loc[i, 't '+cds[0]] = ''
                        elif book.shift(1).loc[i, 't '+cds[0]] == 'buy' or book.shift(1).loc[i, 't '+cds[0]] == 'ready':
                            book.loc[i, 't '+cds[0]] = 'buy'  
                        else:
                            book.loc[i, 't '+cds[0]] = ''  
                        
                elif sample.loc[i, 'lb'] >= price:
                    if book.shift(1).loc[i, 't '+cds[0]] == 'buy':    # 이미 매수상태라면
                        book.loc[i, 't '+cds[0]] = 'buy'     # 매수상태 유지
                    else:
                        if buy == 'in':   # 밴드 진입 시 매수
                            book.loc[i, 't '+cds[0]] = 'ready'    # 대기
                        else:
                            book.loc[i, 't '+cds[0]] = 'buy'     # 매수
            
            else:
   
                if price > sample.loc[i, thd]:
                    book.loc[i, 't '+cds[0]] = ''
                elif sample.loc[i, thd] >= price and price >= sample.loc[i, 'lb']:
                    if book.shift(1).loc[i, 't '+cds[0]] == 'buy' or book.shift(1).loc[i, 't '+cds[0]] == 'ready':
                        book.loc[i, 't '+cds[0]] = 'buy'
                    else:
                        book.loc[i, 't '+cds[0]] = ''
                elif sample.loc[i, 'lb'] > price:
                    if book.shift(1).loc[i, 't '+cds[0]] == 'buy':    # 이미 매수상태라면
                        book.loc[i, 't '+cds[0]] = 'buy'     # 매수상태 유지
                    else:
                        if buy == 'in':   # 밴드 진입 시 매수
                            book.loc[i, 't '+cds[0]] = 'ready'    # 대기
                        else:
                            book.loc[i, 't '+cds[0]] = 'buy'     # 매수
                  
        return (book) 
    
    
    
    def trading_strategy(self, sample, thd, s_cd, last_date):
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        i = sample.index[-1]
        if sample.loc[i, cds[0]] >= sample.loc[i, thd]:
            strategy = ''
        elif sample.loc[i, cds[0]] <= sample.loc[i, 'lb']:
            strategy = 'buy '+cds[0]
        else:
            strategy = 'just wait'
        print ('As of', last_date, 'this model suggests you to', strategy)    
        return (strategy)     
    
    
    def expected_y(self, sample, s_cd, r, d, t, T):
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd
            
        from finterstellar import Valuation
        vu = Valuation()
        for i in sample.index:
            sample.loc[i, cds[1]+' expected'] = vu.futures_price(sample.loc[i, cds[0]], r, d, t, T)
        sample[cds[1]+' spread'] = sample[cds[1]] - sample[cds[1]+' expected']
        return (sample)

    
    
class IntradayOptionsTradeOnValue(IntradayTrade):
    
    
    def expected_y(self, sample, s_codes, K, t, T, r, sigma):
        from finterstellar import Valuation
        vu = Valuation()
        ttm = vu.time_to_maturity(t, T)
        for i in sample.index:
            sample.loc[i, s_codes[1]+' expected'] = vu.call_price(sample.loc[i, s_codes[0]], K, ttm, r, sigma)
            # S, K, ttm, r, sigma
        sample[s_codes[1]+' spread'] = sample[s_codes[1]] - sample[s_codes[1]+' expected']
        return (sample)

    
    
    def price_analyze(self, sample, thd, s_codes):
        for i in sample.index:
            threshold = float( thd * sample.loc[i, s_codes[1]] )
            if sample.loc[i, s_codes[1]+' spread'] > 0:
                sample.loc[i, 'cheaper'] = s_codes[0]
            elif sample.loc[i, s_codes[1]+' spread'] < -threshold:
                sample.loc[i, 'cheaper'] = s_codes[1]
            else:
                sample.loc[i, 'cheaper'] = 'E'
        print(sample.groupby('cheaper').count())
        return (sample)
    
    
    def tradings(self, sample, book, thd, s_codes):
        for i in sample.index:
            threshold = float( thd * sample.loc[i, s_codes[1]] )
            if sample.loc[i, s_codes[1]+' spread'] > threshold:
                book.loc[i, 't '+s_codes[1]] = 'sell'
            elif threshold >= sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= 0:
                book.loc[i, 't '+s_codes[1]] = 'sell'
            elif 0 > sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= -threshold:
                book.loc[i, 't '+s_codes[1]] = ''
            elif -threshold > sample.loc[i, s_codes[1]+' spread']:
                book.loc[i, 't '+s_codes[1]] = 'buy'
        return (book) 
    
    
    def trading_strategy(self, sample, thd, s_codes, last_date):
        i = sample.index[-1]
        threshold = float( thd * sample.loc[i, s_codes[1]] )
        
        if sample.loc[i, s_codes[1]+' spread'] > threshold:
            strategy = 'sell '+s_codes[1]
        elif threshold >= sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= 0:
            strategy = 'sell '+s_codes[1]
        elif 0 > sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= -threshold:
            strategy = 'do nothing'
        elif -threshold > sample.loc[i, s_codes[1]+' spread']:
            strategy = 'buy '+s_codes[1]

        print ('As of', last_date, 'this model suggests you to', strategy)
        return (strategy) 
    
