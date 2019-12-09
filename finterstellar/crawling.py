import bs4
from urllib.request import urlopen
#import datetime as dt
import pandas as pd
import re
import json


class Naver:
    
    def date_format(self, d=''):
        if d != '':
            this_date = pd.to_datetime(d).date()
        else:
            this_date = pd.Timestamp.today().date()   # 오늘 날짜를 지정
        return (this_date)
    

    
    def stock_price(self, historical_prices, stock_cd, start_date='', end_date='', page_n=1, last_page=0):

        #nvr = self.NaverPrice()
        start_date = self.date_format(start_date)
        end_date = self.date_format(end_date)

        naver_stock = 'http://finance.naver.com/item/sise_day.nhn?code=' + stock_cd + '&page=' + str(page_n)

        source = urlopen(naver_stock).read()
        source = bs4.BeautifulSoup(source, 'lxml')

        dates = source.find_all('span', class_='tah p10 gray03')   # 날짜 수집   
        prices = source.find_all('td', class_='num')   # 종가 수집
        
        for n in range(len(dates)):

            if len(dates) > 0:

                # 날짜 처리
                this_date = dates[n].text
                this_date = self.date_format(this_date)

                if this_date <= end_date and this_date >= start_date:   
                # start_date와 end_date 사이에서 데이터 저장
                    # 종가 처리
                    this_close = prices[n*6].text
                    this_close = this_close.replace(',', '')
                    this_close = float(this_close)

                    # 딕셔너리에 저장
                    historical_prices[this_date] = this_close

                elif this_date < start_date:   
                # start_date 이전이면 함수 종료
                    return (historical_prices)              

        # 페이지 네비게이션
        if last_page == 0:
            last_page = source.find_all('table')[1].find('td', class_='pgRR').find('a')['href']
            last_page = last_page.split('&')[1]
            last_page = last_page.split('=')[1]
            last_page = float(last_page)

        # 다음 페이지 호출
        if page_n < last_page:
            page_n = page_n + 1
            self.stock_price(historical_prices, stock_cd, start_date, end_date, page_n, last_page)   

        return (historical_prices)


    def index_korea(self, historical_prices, index_cd, start_date='', end_date='', page_n=1, last_page=0):
    
        start_date = self.date_format(start_date)
        end_date = self.date_format(end_date)

        naver_index = 'http://finance.naver.com/sise/sise_index_day.nhn?code=' + index_cd + '&page=' + str(page_n)

        source = urlopen(naver_index).read()   # 지정한 페이지에서 코드 읽기
        source = bs4.BeautifulSoup(source, 'lxml')   # 뷰티풀 스프로 태그별로 코드 분류

        dates = source.find_all('td', class_='date')   # <td class="date">태그에서 날짜 수집   
        prices = source.find_all('td', class_='number_1')   # <td class="number_1">태그에서 지수 수집

        for n in range(len(dates)):

            if dates[n].text.split('.')[0].isdigit():

                # 날짜 처리
                this_date = dates[n].text
                this_date= self.date_format(this_date)

                if this_date <= end_date and this_date >= start_date:   
                # start_date와 end_date 사이에서 데이터 저장
                    # 종가 처리
                    this_close = prices[n*4].text   # prices 중 종가지수인 0,4,8,...번째 데이터 추출
                    this_close = this_close.replace(',', '')
                    this_close = float(this_close)

                    # 딕셔너리에 저장
                    historical_prices[this_date] = this_close

                elif this_date < start_date:   
                # start_date 이전이면 함수 종료
                    return (historical_prices)              

        # 페이지 네비게이션
        if last_page == 0:
            last_page = source.find('td', class_='pgRR').find('a')['href']
            # 마지막페이지 주소 추출
            last_page = last_page.split('&')[1]   # & 뒤의 page=506 부분 추출
            last_page = last_page.split('=')[1]   # = 뒤의 페이지번호만 추출
            last_page = int(last_page)   # 숫자형 변수로 변환

        # 다음 페이지 호출
        if page_n < last_page:   
            page_n = page_n + 1   
            self.index_korea(historical_prices, index_cd, start_date, end_date, page_n, last_page)   

        return (historical_prices)  
    
    # 구성종목 기본정보
    def stock_info(self, stock_cd):
        url_float = 'http://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd=' + stock_cd
        source = urlopen(url_float).read()
        soup = bs4.BeautifulSoup(source, 'lxml')

        tmp = soup.find(id='cTB11').find_all('tr')[6].td.text
        tmp = tmp.replace('\r', '')
        tmp = tmp.replace('\n', '')
        tmp = tmp.replace('\t', '')

        tmp = re.split('/', tmp)

        outstanding = tmp[0].replace(',', '')
        outstanding = outstanding.replace('주', '')
        outstanding = outstanding.replace(' ', '')
        outstanding = int(outstanding)

        floating = tmp[1].replace(' ', '')
        floating = floating.replace('%', '')
        floating = float(floating)

        name = soup.find(id='pArea').find('div').find('div').find('tr').find('td').find('span').text

        #k10_outstanding[stock_cd] = outstanding
        #k10_floating[stock_cd] = floating
        #k10_name[stock_cd] = name    
        
        return (name, outstanding, floating)

    
    
    def index_global(self, d, symbol, start_date='', end_date='', page=1):

        end_date = self.date_format(end_date)
        if start_date == '':
            start_date = end_date - pd.DateOffset(years=1)
        start_date = self.date_format(start_date)

        url = 'https://finance.naver.com/world/worldDayListJson.nhn?symbol='+symbol+'&fdtc=0&page='+str(page)
        raw = urlopen(url)
        data = json.load(raw)

        if len(data) > 0:

            for n in range(len(data)):
                date = pd.to_datetime(data[n]['xymd']).date()

                if date <= end_date and date >= start_date:   
                # start_date와 end_date 사이에서 데이터 저장
                    # 종가 처리
                    price = float(data[n]['clos'])
                    # 딕셔너리에 저장
                    d[date] = price
                elif date < start_date:   
                # start_date 이전이면 함수 종료
                    return (d)              

            if len(data) == 10:
                page += 1
                self.index_global(d, symbol, start_date, end_date, page)

        return (d)
    
    
class NaverStockInfo:
    
    def read_src(self, stock_cd):
        url_float = 'http://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd=' + stock_cd
        source = urlopen(url_float).read()
        soup = bs4.BeautifulSoup(source, 'lxml')
        return (soup)
        
    
    def stock_info(self, stock_cd):
        url_float = 'http://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd=' + stock_cd
        source = urlopen(url_float).read()
        soup = bs4.BeautifulSoup(source, 'lxml')

        tmp = soup.find(id='cTB11').find_all('tr')[6].td.text
        tmp = tmp.replace('\r', '')
        tmp = tmp.replace('\n', '')
        tmp = tmp.replace('\t', '')

        tmp = re.split('/', tmp)

        outstanding = tmp[0].replace(',', '')
        outstanding = outstanding.replace('주', '')
        outstanding = outstanding.replace(' ', '')
        outstanding = int(outstanding)

        floating = tmp[1].replace(' ', '')
        floating = floating.replace('%', '')
        floating = float(floating)

        name = soup.find(id='pArea').find('div').find('div').find('tr').find('td').find('span').text
       
        return (name, outstanding, floating)
    
    def outstanding(self, stock_cd):
        soup = self.read_src(stock_cd)
        tmp = soup.find(id='cTB11').find_all('tr')[6].td.text
        tmp = tmp.replace('\r', '')
        tmp = tmp.replace('\n', '')
        tmp = tmp.replace('\t', '')
        tmp = re.split('/', tmp)
        outstanding = tmp[0].replace(',', '')
        outstanding = outstanding.replace('주', '')
        outstanding = outstanding.replace(' ', '')
        outstanding = int(outstanding)
        return (outstanding)
    
    def floating(self, stock_cd):
        soup = self.read_src(stock_cd)
        tmp = soup.find(id='cTB11').find_all('tr')[6].td.text
        tmp = tmp.replace('\r', '')
        tmp = tmp.replace('\n', '')
        tmp = tmp.replace('\t', '')
        tmp = re.split('/', tmp)
        floating = tmp[1].replace(' ', '')
        floating = floating.replace('%', '')
        floating = float(floating)
        return (floating)
    
    def floating(self, stock_cd):
        soup = self.read_src(stock_cd)
        tmp = soup.find(id='cTB11').find_all('tr')[6].td.text
        tmp = tmp.replace('\r', '')
        tmp = tmp.replace('\n', '')
        tmp = tmp.replace('\t', '')
        tmp = re.split('/', tmp)
        floating = tmp[1].replace(' ', '')
        floating = floating.replace('%', '')
        floating = float(floating)
        return (floating)
    
    def float_convert(self, s):
        try:
            s = s.replace(' ', '')
            s = s.replace(',', '')
            if re.findall('억', s):
                m = 100000000
                s = s.replace('억', '')
            elif re.findall('백만', s):
                m = 1000000
                s = s.replace('백만', '')
            if re.findall('%', s):
                m = 0.01
                s = s.replace('%', '')
            s = s.replace('원', '')
            f = float(s) * m
        except:
            f = s
        return (f)
    
    def fundamentals(self, stock_cd, f):
        factors = dict()
        soup = self.read_src(stock_cd)
        rows = len(soup.find_all('div', class_='fund fl_le')[0].find_all('tr'))
        for r in range(1, rows, 1):
            title = soup.find_all('div', class_='fund fl_le')[0].find_all('tr')[r].find_all('th')[0].text
            value_current = soup.find_all('div', class_='fund fl_le')[0].find_all('tr')[r].find_all('td')[0].text
            value_current = self.float_convert(value_current)
            value_estimated = soup.find_all('div', class_='fund fl_le')[0].find_all('tr')[r].find_all('td')[1].text
            value_estimated = self.float_convert(value_estimated)
            factors[title] = [value_current, value_estimated]
            print(title, value_current, value_estimated)
        return (factors[f])
    
class DART:
    def disclosure_search(self, auth_key, cd, base_date):
        url_search = 'http://dart.fss.or.kr/api/search.json?auth='+auth_key+'&crp_cd='+cd+'&start_dt='+base_date+'&bsn_tp=A001'

        raw = urlopen(url_search)
        data = json.load(raw)

        rcp_no = data['list'][0]['rcp_no']
        return(rcp_no)
    
    def view_doc(self, rcp_no):
        url_doc = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo='+rcp_no

        source = urlopen(url_doc).read()
        soup = bs4.BeautifulSoup(source, 'lxml')

        tmp = soup.find_all('script')[7].text
        menu = tmp.split('new Tree.TreeNode')

        i = 0
        for m in menu:
            if re.search(' 재무제표"', m):
                num = i
            i += 1

        prop = menu[num].split('click: function() {viewDoc(')[1]
        prop = prop.split(');}')[0]
        prop = prop.replace("'", "")
        prop = prop.replace(' ', '')
        prop = prop.split(',')

        return(prop)
    
    
    def extract_fn_item(self, item, p0, p1, p2, p3, p4):
        url_stmt = 'http://dart.fss.or.kr/report/viewer.do?rcpNo='+p0+'&dcmNo='+p1+'&eleId='+p2+'&offset='+p3+'&length='+p4+'&dtd=dart3.xsd'
        #print(url_stmt)
        source = urlopen(url_stmt).read()
        soup = bs4.BeautifulSoup(source, 'lxml')
        stmt = soup.find_all('tr')

        i = 0
        ss = []
        for s in stmt:
            if re.search(item, str(s)):
                ss.append(i)
            i += 1

        titles = []
        for s in ss:
            itm = stmt[s]
            itm = itm.find_all('td')

            if len(itm)>=1:
                itm_title = itm[0]
                txt = ''
                for t in itm_title.stripped_strings:
                    pass
                itm_title = t
                titles.append(itm_title)

                if itm_title == item:
                    s_num = s
                elif re.search(r'\(', itm_title):
                    if itm_title.split('(')[0] == item:
                        s_num = s

        itm = stmt[s_num]
        itm = itm.find_all('td')

        itm_title = itm[0].find('p').text
        itm_title = itm_title.replace('\u3000', '')

        itm_figure = itm[1].find('p').text
        itm_figure = itm_figure.replace(',', '')
        itm_figure = float(itm_figure)

        return(itm_title, itm_figure)
    
    
    def extract_unit(self, p0, p1, p2, p3, p4):
        url_stmt = 'http://dart.fss.or.kr/report/viewer.do?rcpNo='+p0+'&dcmNo='+p1+'&eleId='+p2+'&offset='+p3+'&length='+p4+'&dtd=dart3.xsd'
        #print(url_stmt)
        source = urlopen(url_stmt).read()
        soup = bs4.BeautifulSoup(source, 'lxml')
        stmt = soup.find_all('tr')

        i = 0
        for s in stmt:
            if re.search('단위', str(s)):
                u_num = i
            i += 1
        unit = stmt[u_num]
        unit = unit.find_all('td')
        if len(unit) > 1:
            unit = unit[1].text
        else:
            unit = unit[0].text
        unit = unit.split(':')
        unit = unit[1]
        try:
            unit = unit.replace(')', '')
        except:
            pass
        try:
            unit = unit.replace(' ', '')
        except:
            pass
        try:
            unit = unit.replace('\n', '')
        except:
            pass

        if unit == '백만원':
            unit_num = 1000000
        elif unit == '천원':
            unit_num = 1000
        else:
            unit_num = 1

        return(unit, unit_num)
    
    
    def extract_fn_stmt(self, p0, p1, p2, p3, p4):
        url_stmt = 'http://dart.fss.or.kr/report/viewer.do?rcpNo='+p0+'&dcmNo='+p1+'&eleId='+p2+'&offset='+p3+'&length='+p4+'&dtd=dart3.xsd'
        source = urlopen(url_stmt).read()
        soup = bs4.BeautifulSoup(source, 'lxml')
        stmt = soup.find_all('tr')

        fn_stmt_dict = {}
        for r in range(len(stmt)):
            try:
                columns = []
                for c in stmt[r].find_all('td'):
                    for t in c.stripped_strings:
                        t = t.replace(' \xa0', '')
                        t = t.replace(' ', '')
                        t = t.replace(',', '')
                        t = re.sub('\s', '', t)
                        # 0 처리
                        t = re.sub('^-$', '0', t)
                        # 음수처리
                        if re.match('\(', t):
                            t = t.replace('(', '')
                            t = t.replace(')', '')
                            try:
                                t = float(t)
                            except:
                                pass
                            t = t * -1
                        try:
                            t = float(t)
                        except:
                            pass
                        columns.append(t)

            except:
                pass

           # 계정과목명 정제
            if len(columns) > 3:
                col_len = len(columns)
                col_iter = 1
                while col_iter <= col_len:
                    columns[0] = re.sub('[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩXIVxiv\d]+\.', '', columns[0])   # 로마숫자 제거
                    if not type(columns[1]) == float:   # 텍스트 합체
                        columns[0] += columns[1]
                        del columns[1]
                        col_len -= 1
                    col_iter += 1

            # print(len(columns), columns)
            if len(columns) == 4:
                fn_stmt_dict[columns[0]] = columns[1:4]

        fn_stmt = pd.DataFrame.from_dict(fn_stmt_dict, orient='index', columns=['당기', '전기', '전전기'])

        return(fn_stmt)

    
    
class FnGuide:
    
    def fn_stmt(self, cd, i):
        rows = {}

        url = 'https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A'+cd+'&cID=&MenuYn=Y&ReportGB=D&NewMenuID=103&stkGb=701'
        source = urlopen(url).read()
        soup = bs4.BeautifulSoup(source, 'lxml')

        tbl = soup.find_all('table')[i]
        tr = tbl.find_all('tr')
        n_tr = len(tr)

        for r in range(n_tr):
            td = tr[r]
            n_th = len(td.find_all('th'))
            n_td = len(td.find_all('td'))

            cols = []
            for n in range(n_th):
                t = td.find_all('th')[n].text
                t = self.fin_stmt_refine(t)
                cols.append(t)
            for n in range(n_td):
                t = td.find_all('td')[n].text
                t = self.fin_stmt_refine(t)
                cols.append(t)

            rows[cols[0]] = cols[1:]

        df = pd.DataFrame.from_dict(rows, orient='index')
        df.columns = df.iloc[0]
        df = df[1:]

        return(df)
    
    
    def fn_ratio(self, cd, i):

        rows = {}

        url_ratio = 'https://comp.fnguide.com/SVO2/ASP/SVD_FinanceRatio.asp?pGB=1&gicode=A'+cd+'&cID=&MenuYn=Y&ReportGB=&NewMenuID=104&stkGb=701'
        source = urlopen(url_ratio).read()
        soup = bs4.BeautifulSoup(source, 'lxml')

        tbl = soup.find_all('table')[i]
        tr = tbl.find_all('tr')
        n_tr = len(tr)

        for r in range(n_tr):

            td = tr[r]
            n_th = len(td.find_all('th'))
            n_td = len(td.find_all('td'))

            if n_th+n_td > 1 :

                cols = []
                for n in range(n_th):
                    t = td.find_all('th')[n].text
                    t = self.fin_stmt_refine(t)
                    try:   # 텍스트 정제
                        t = re.sub('계산에참여한계정펼치기', '', t)
                        txt = re.split('\(', t)[0]
                        tmp = re.search(txt, t[1:]).span()[0]
                        t = t[:tmp+1]
                    except:
                        pass
                    cols.append(t)
                for n in range(n_td):
                    t = td.find_all('td')[n].text
                    t = self.fin_stmt_refine(t)
                    cols.append(t)

                rows[cols[0]] = cols[1:]

        df = pd.DataFrame.from_dict(rows, orient='index')
        df.columns = df.iloc[0]
        df = df[1:]

        return(df)    
    
    
    def fin_stmt_refine(self, t):
        t = re.sub('\s', '', t)
        t = re.sub('^-$', '0', t)   # 0 처리
        t = re.sub(',', '', t)
        if re.match('\(', t):   # 음수처리
            t = t.replace('(', '')
            t = t.replace(')', '')
            try:
                t = float(t)
            except:
                pass
            t = t * -1

        try:
            t = float(t)
        except:
            pass

        return(t)    