#coding:utf8
from __future__ import print_function
import sys
import numpy as np

class Grid:
    def __init__(self):
        self.begin = False
        self.last_price = None
        pass
    def __call__(self, market):
        
        N = 10
        p = 0.1
        price = market.price[0]
        if self.begin == False:
            self.trigger = {}
            self.begin = True
            self.baseprice = market.price[0]
            for i in range(-N, 1+N):
                self.trigger[i] = ['buy']
            
            return [0]
        
        delta = 0
        if self.last_price :
            for k, v in self.trigger.items():
                if (v and ((1+p)**k * self.baseprice < self.last_price and (1+p)**k * self.baseprice > price
                    or
                    (1+p)**k * self.baseprice > self.last_price and (1+p)**k * self.baseprice < price)):
                    
                    
                    for action in v :
                        if action == 'buy':
                            delta += 1
                            if k + 1 not in self.trigger : self.trigger[k+1]=[]
                            self.trigger[k+1].append('sell')
                        if action == 'sell':
                            delta -= 1
                            if k - 1 not in self.trigger : self.trigger[k-1]=[]
                            self.trigger[k-1].append('buy')
                    self.trigger[k] = []
                    break
                    
                            
            pass
        self.last_price = price
        return [delta]

class B2:
    def __init__(self):
        pass
    def __call__(self, market):
        if market.hold[0] == 0:
            self.base = market.price[0]
            print(self.base)
            return [1]
        
        self.base *= 1.0000
        if (market.hold[0] * market.price[0] > self.base * 1.2 
            or market.hold[0] * market.price[0] < self.base * 0.8):
            delta = self.base / market.price[0] - market.hold[0]
            return [delta]
        return [0]
    
class Balance:
    def __init__(self):
        self.cash_price = 1
        self.cash_hold = 0
        pass
    def __call__(self, market):
        #print(market.hold)
        if market.hold[0] == 0:
            cash = 1.0
            self.n = len(market.hold)
            
            buy = [cash / (self.n + 1) / market.price[i] for i in range(self.n)]
            self.cash_hold = cash / (self.n + 1)
            
            return buy
        
        #self.cash_hold *= 1.0002
        value = [self.cash_hold]
        for i in range(self.n):
            value.append(market.hold[i] * market.price[i])
        
        #print(max(value), min(value))
        if max(value) / min(value) > 1.1 :
            cash = sum(value)
            
            cash = sum(value)
            self.n = len(market.hold)
            
            buy = [cash / (self.n + 1) / market.price[i] for i in range(self.n)]
            self.cash_hold = cash / (self.n + 1)
            
            for i in range(len(buy)):
                buy[i] = buy[i] - market.hold[i]
            #print(buy)
            return buy
        
        return [0 for i in range(self.n)]

import random
class Rand:
    def __init__(self):
        pass
    def __call__(self, market):
        if market.hold == 0:
            self.cash = market.price
            print(self.cash)
            return 1
        self.cash *= 1.0002
        if random.random() < 0.001:
            delta = (self.cash + market.hold * market.price) / 2 / market.price - market.hold
            #print(market.date, market.hold, market.price, self.cash, delta * market.price)
            self.cash -= market.price * delta
            return delta
        return 0
    

class Adam_Mean:
    def __init__(self):
        self.n = 0
        self.alpha = 0.9
        self.beta = 0.999
        self.eta = 0.008
        self.t = 0
        self.v = None
        self.m = 0
        self.q = 0
        self.ma = 0
    def __call__(self, p):
        if self.v is None:
            self.v = p
            self.ma = p
            return self.v, 0
        self.t += 1
        d = p - self.v
        self.m = self.alpha * self.m + (1 - self.alpha) * d
        self.q = self.beta * self.q + (1 - self.beta) * d * d
        mh = self.m / (1 - self.alpha ** self.t)
        qh = self.q / (1 - self.beta ** self.t)
        self.v += self.eta * mh / (np.sqrt(qh) + 0.0000001) * self.v
        self.ma = 0.99 * self.ma + 0.01 * p
        return self.v, np.sqrt(qh)

class AdamPolicy:
    def __init__(self):
        self.adam = Adam_Mean()
        self.last_adam = None
        self.last_price = None
        self.t = 0
        pass
    def __call__(self, market):
        #print('adam')
        price = market.price[0]
        hold = market.hold[0]
        a, _ = self.adam(price)
        delta = 0
        if self.last_adam is None:
            pass
        else :
            
            
            
            """if abs((a - self.last_adam) / self.last_adam) < 0.:
                delta = -hold
                pass
            else :
                if (a < price):
                    delta = 1.0 / price - hold
                if (a > price):
                    delta = -1.0 / price - hold"""
            if (self.last_adam > self.last_price) and (a < price):
                delta = 1.0 / price - hold
            if (self.last_adam < self.last_price) and (a > price):
                delta = -1.0 / price - hold
            
            
                
        self.last_price = price
        self.last_adam = a
            
        return [delta]
        
def gen_adam(line):
    am = Adam_Mean()
    adam = []
    ss = []
    for p in (line[:]):
        a, s = am(p)
        adam.append(a)
        ss.append(s)
        
    return np.array(adam), np.array(ss)
