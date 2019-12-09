import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from scipy import stats 


class Valuation:
    
    def time_to_maturity(self, t0, T, y=252):
        t0 = pd.to_datetime(t0).date()
        T = pd.to_datetime(T).date()
        return ( np.busday_count(t0, T) / y )

    
    def ddm(self, d, r, g):
        p = d / (r - g)
        return(p)
    
    
    def dcf(self, r, *cf):
        n = 1
        p = 0
        for c in cf:
            p += (c / (1+r)**n)
            n += 1
        return(p)


    def futures_price(self, S, r, d, t0, T):
        #ttm = np.busday_count(t0, T) / 252
        ttm = self.time_to_maturity(t0, T)
        F = S * np.exp((r-d)*ttm)
        return (F)

    
    def call_price(self, S, K, ttm, r, sigma):    
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        d2 = ( np.log(S / K) + (r - sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = ( S * stats.norm.cdf(d1, 0.0, 1.0) ) - K * np.exp( -r * ttm ) * stats.norm.cdf(d2, 0.0, 1.0)
        return val
    

    def put_price(self, S, K, ttm, r, sigma):    
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        d2 = ( np.log(S / K) + (r - sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = K * np.exp( -r * ttm ) * stats.norm.cdf(-d2, 0.0, 1.0) - ( S * stats.norm.cdf(-d1, 0.0, 1.0) ) 
        return val
    
    
    def call_delta(self, S, K, ttm, r, sigma):
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = stats.norm.cdf(d1, 0.0, 1.0)
        return val

    
    def put_delta(self, S, K, ttm, r, sigma):
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = stats.norm.cdf(d1, 0.0, 1.0)  - 1
        return val

    
    def ndx(self, x):
        return ( np.exp( -1 * x**2 * 0.5 ) / np.sqrt(2 * np.pi) )
    
    
    def gamma(self, S, K, ttm, r, sigma):
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = ( self.ndx(d1) ) / ( S * sigma * np.sqrt(ttm) )
        return val
    
    
    def call_theta(self, S, K, ttm, r, sigma):    
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        d2 = ( np.log(S / K) + (r - sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = -1 * ( ( S * self.ndx(d1) * sigma ) / ( 2 * np.sqrt(ttm)) ) - r * K * np.exp(-r*ttm) * stats.norm.cdf(d2, 0.0, 1.0)
        return val
    
    
    def put_theta(self, S, K, ttm, r, sigma):    
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        d2 = ( np.log(S / K) + (r - sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = -1 * ( ( S * self.ndx(d1) * sigma ) / ( 2 * np.sqrt(ttm)) ) + r * K * np.exp(-r*ttm) * stats.norm.cdf(-1*d2, 0.0, 1.0)
        return val
    
    
    def vega(self, S, K, ttm, r, sigma):    
        d1 = ( np.log(S / K) + (r + sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        d2 = ( np.log(S / K) + (r - sigma**2 * 0.5) * ttm ) / ( sigma * np.sqrt(ttm) )
        val = ( S * np.sqrt(ttm) * self.ndx(d1) )
        return val
    
    def implied_vol_call(self, S, K, ttm, r, sigma, C, repeat=100):
        for i in range(repeat):
            sigma = sigma - ( (self.call_price(S, K, ttm, r, sigma) - C) / self.vega(S, K, ttm, r, sigma) )
        return sigma
    
    def implied_vol_put(self, S, K, ttm, r, sigma, P, repeat=100):
        for i in range(repeat):
            sigma = sigma - ( (self.put_price(S, K, ttm, r, sigma) - P) / self.vega(S, K, ttm, r, sigma) )
        return sigma
    
    

class ValueAtExpiry:
    
    def stock(self, x, x0):
        y = x - x0
        return y

    def x_axis(self, x):
        return x*0
    
    def futures(self, s, k):
        return s - k
    
    def call_option(self, s, k, p):
        return np.where(s > k, s - k - p, -p)
    
    def put_option(self, s, k, p):
        return np.where(s < k, k - s - p, -p)
    
    def ko_put(self, s, k, b, p):
        return np.where(s > b, np.where(s > k, -p, k - s - p), -p)
    
    def ki_call(self, s, k, b, p):
        return np.where(s > b, np.where(s > k, s - k - p, -p), -p)
    
    def synthetic(self, x, **y):
        s = pd.Series(0 for _ in range(len(x)))
        for key, value in y.items():
            s = s + pd.Series(value)
        return (s)