import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression



class PairAnalyze:
    
    def regression(self, sample, s_codes):
        sample.dropna(inplace=True)
        x = sample[s_codes[0]]
        y = sample[s_codes[1]]
        # 1개 컬럼 np.array로 변환
        x = np.array(x).reshape(-1, 1)
        y = np.array(y).reshape(-1, 1)
        # Linear Regression
        regr = LinearRegression()
        regr.fit(x, y)
        result = {'Slope':regr.coef_[0,0], 'Intercept':regr.intercept_[0], 'R2':regr.score(x, y) }
        #result = {'Slope':regr.coef_, 'Intercept':regr.intercept_, 'R2':regr.score(x, y) }
        return(result)
    
    
    def compare_r2(self, prices_df, base_date, s_codes):
        comp_df = pd.DataFrame()
        s_df = self.sampling(prices_df, base_date, s_codes)
        s_df = s_df.dropna()
        n = len(s_codes)
        for i in range(0, n, 1):
            for j in range(i, n, 1):
                if i != j:
                    code_pairs = [ s_codes[i], s_codes[j] ]
                    regr = self.regression(s_df, code_pairs)
                    c_pair = s_codes[i]+' vs. '+s_codes[j]
                    #print(s_codes[i], '-', s_codes[j], ' : ', '{:,.2f}'.format(regr['R2']*100))
                    comp_df.loc[c_pair, 'R2'] = round(regr['R2'], 4)
                    comp_df.loc[c_pair, 'Slope'] = round(regr['Slope'], 4)
        comp_df.index.name = 'pair'
        comp_df = comp_df.sort_values(by='R2', ascending=False)
        return (comp_df)

    
    def compare_r2_dict(self, prices_df, base_date, cd_dict):
        comp_df = pd.DataFrame()
        s_codes = list(cd_dict.keys())
        s_names = list(cd_dict.values())
        s_df = self.sampling(prices_df, base_date, s_codes)
        s_df = s_df.dropna()
        n = len(s_codes)
        for i in range(0, n, 1):
            for j in range(i, n, 1):
                if i != j:
                    code_pairs = [ s_codes[i], s_codes[j] ]
                    regr = self.regression(s_df, code_pairs)
                    c_pair = s_codes[i]+' vs. '+s_codes[j]
                    #print(s_codes[i], '-', s_codes[j], ' : ', '{:,.2f}'.format(regr['R2']*100))
                    comp_df.loc[c_pair, 'R2'] = round(regr['R2'], 4)
                    comp_df.loc[c_pair, 'Slope'] = round(regr['Slope'], 4)
                    comp_df.loc[c_pair, 'X code'] = s_codes[i]
                    comp_df.loc[c_pair, 'Y code'] = s_codes[j]
                    comp_df.loc[c_pair, 'X name'] = s_names[i]
                    comp_df.loc[c_pair, 'Y name'] = s_names[j]
        comp_df.index.name = 'pair'
        comp_df = comp_df.sort_values(by='R2', ascending=False)
        return (comp_df)
    
    
    def regression_rolling(self, sample, code_pair, period=60, step=10):
        result_dict = {}
        R2_lst = []

        sample.dropna(inplace=True)
        sample_size = len(sample)

        if sample_size > period:
            for i in range(0, sample_size, step):
                sub_sample = sample.iloc[i:i+period].copy()
                x = sub_sample[code_pair[0]]
                y = sub_sample[code_pair[1]]
                # 1개 컬럼 np.array로 변환
                x = np.array(x).reshape(-1, 1)
                y = np.array(y).reshape(-1, 1)
                # Linear Regression
                regr = LinearRegression()
                regr.fit(x, y)
                result_dict[i] = [regr.coef_[0,0], regr.intercept_[0], regr.score(x, y)]
                # slope, intercept, R2
                R2_lst.append(regr.score(x, y))
        else:
            x = sample[code_pair[0]]
            y = sample[code_pair[1]]
            # 1개 컬럼 np.array로 변환
            x = np.array(x).reshape(-1, 1)
            y = np.array(y).reshape(-1, 1)
            # Linear Regression
            regr = LinearRegression()
            regr.fit(x, y)
            result_dict[0] = [regr.coef_[0,0], regr.intercept_[0], regr.score(x, y)]
            R2_lst.append(regr.score(x, y))

        R2_mean = round(np.mean(R2_lst), 4)    # mean
        R2_std = round(np.std(R2_lst), 4)    # standard deviation
        return (R2_mean, R2_std, result_dict)

    
    
    def compare_r2_rolling(self, prices_df, cd_dict, period=60, step=5):
        comp_df = pd.DataFrame()
        s_codes = list(cd_dict.keys())
        s_names = list(cd_dict.values())
        s_df = prices_df.dropna()
        n = len(s_codes)
        for i in range(0, n, 1):
            for j in range(i, n, 1):
                if i != j:
                    cp = ( s_codes[i], s_codes[j] )
                    rr = self.regression_rolling(s_df, cp, period, step)
                    c_pair = s_codes[i]+' vs. '+s_codes[j]
                    #print(s_codes[i], '-', s_codes[j], ' : ', '{:,.2f}'.format(regr['R2']*100))
                    comp_df.loc[c_pair, 'R2 mean'] = round(rr[0], 4)
                    comp_df.loc[c_pair, 'R2 std'] = round(rr[1], 4)
                    comp_df.loc[c_pair, 'X code'] = s_codes[i]
                    comp_df.loc[c_pair, 'Y code'] = s_codes[j]
                    comp_df.loc[c_pair, 'X name'] = s_names[i]
                    comp_df.loc[c_pair, 'Y name'] = s_names[j]
        comp_df.index.name = 'pair'
        comp_df = comp_df.sort_values(by='R2 mean', ascending=False)
        return (comp_df)
    
    
        
    def expected_y(self, sample, regr, s_codes):
        sample[s_codes[1]+' expected'] = sample[s_codes[0]] * regr['Slope'] + regr['Intercept']
        sample[s_codes[1]+' spread'] = sample[s_codes[1]] - sample[s_codes[1]+' expected']
        return (sample)
    
    
    def price_analyze(self, sample, thd, s_codes):
        for i in sample.index:
            threshold = float( thd * sample.loc[i, s_codes[1]] )
            if sample.loc[i, s_codes[1]+' spread'] > threshold:
                sample.loc[i, 'cheaper'] = s_codes[0]
            elif sample.loc[i, s_codes[1]+' spread'] < -threshold:
                sample.loc[i, 'cheaper'] = s_codes[1]
            else:
                sample.loc[i, 'cheaper'] = 'E'
        print(sample.groupby('cheaper').count())
        return (sample)
    
    
    def tradings(self, sample, book, thd, s_codes, short=False):
        for i in sample.index:
            threshold = float( thd * sample.loc[i, s_codes[1]] )
            if sample.loc[i, s_codes[1]+' spread'] > threshold:
                book.loc[i, 't '+s_codes[0]] = 'buy'
                if short == True:
                    book.loc[i, 't '+s_codes[1]] = 'sell'
                else:
                    book.loc[i, 't '+s_codes[1]] = ''
            elif threshold >= sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= 0:
                book.loc[i, 't '+s_codes[0]] = ''
                book.loc[i, 't '+s_codes[1]] = ''
            elif 0 > sample.loc[i, s_codes[1]+' spread'] and sample.loc[i, s_codes[1]+' spread'] >= -threshold:
                book.loc[i, 't '+s_codes[0]] = ''
                book.loc[i, 't '+s_codes[1]] = ''
            elif -threshold > sample.loc[i, s_codes[1]+' spread']:
                if short == True:
                    book.loc[i, 't '+s_codes[0]] = 'sell'
                else:
                    book.loc[i, 't '+s_codes[0]] = ''
                book.loc[i, 't '+s_codes[1]] = 'buy'       
        return (book) 