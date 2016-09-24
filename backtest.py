#coding:utf8
from __future__ import print_function
import sys
import numpy as np

class Market :
    def __init__(self):
        self.hold_vt = 0
        pass
    def get_current_value(self, use_abs = False):
        value = 0
        for i in range(self.n):
            if use_abs:
                
                value += np.abs(self.hold[i] * self.price[i])
            else :
                value += self.hold[i] * self.price[i]
        return value
    def test(self, data_list, policy):
        
        date_set = None
        data_dict = []
        for data in data_list :
            print(data[0])
            ds = set(d for d, _ in data)
            if date_set is None : 
                date_set = ds
            else:
                date_set |= ds
            data_dict.append({k:v for k, v in data})
        
        #print(len(date_set))
        date_list = sorted(date_set)
        
        self.n = len(data_list)
        self.hold = [0 for i in range(self.n)]
        self.cash = 0
        self.value = []
        last_date = None
        last_value = None
        self.days = (date_list[-1] - date_list[0]).days
        for date in date_list:
            self.date = date
            self.price = [data.get(date, None) for data in data_dict]

            
            #print(date)
            # 计算持有成本
            value = self.get_current_value(use_abs = True)
            if last_date != None :
                days = (date - last_date).days
                self.hold_vt += days * last_value
            last_date = date
            last_value = value
            
            # 计算策略
            deltas = policy(self)
            value = self.cash
            for i in range(self.n):
                if self.price[i] is not None :
                    value += self.hold[i] * self.price[i]
            if sum(abs(d) for d in deltas) != 0 :
                print(date, self.price, self.hold, deltas, self.cash, value, sep = '\t')
                #print(self.hold)
            
            
            for i, delta in enumerate(deltas):
                if self.price[i] is not None :
                    self.cash -= delta * self.price[i]
                    self.hold[i] += delta
            
            # update value
            value = self.cash
            for i in range(self.n):
                if self.price[i] is not None :
                    value += self.hold[i] * self.price[i]
            self.value.append(value)
            
        print(self.cash, self.value[-1])
