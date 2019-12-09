import pandas as pd


class CommonFunctions:
    
    def str_list(s_cd):
        cds = []
        if type(s_cd) == str:
            cds = []
            cds.append(s_cd)
        else:
            cds = s_cd    
        return(cds)   
    
    def date_format(d=''):
        if d != '':
            this_date = pd.to_datetime(d).date()
        else:
            this_date = pd.Timestamp.today().date()   # 오늘 날짜를 지정
        return (this_date)
    
        
    def check_base_date(prices_df, d):
        d = pd.to_datetime(d)
        prices_df.index = pd.to_datetime(prices_df.index)
        if d in pd.to_datetime(prices_df.index):
            return (d)
        else:
            nd = next_date(d)
            d = check_base_date(prices_df, nd)
            return (d)

        
    def next_date(d):
        d = d + pd.DateOffset(1)
        #d += dt.timedelta(1)
        return (d)


class CheckDate:
    
    def date_format(self, d=''):
        if d != '':
            this_date = pd.to_datetime(d).date()
        else:
            this_date = pd.Timestamp.today().date()   # 오늘 날짜를 지정
        return (this_date)
    
        
    def check_base_date(self, prices_df, d):
        d = pd.to_datetime(d)
        prices_df.index = pd.to_datetime(prices_df.index)
        if d in pd.to_datetime(prices_df.index):
            return (d)
        else:
            nd = self.next_date(d)
            d = self.check_base_date(prices_df, nd)
            return (d)

        
    def next_date(self, d):
        d = d + pd.DateOffset(1)
        #d += dt.timedelta(1)
        return (d)