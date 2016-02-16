import math
import requests
import datetime
from collections import Counter
import numpy as np
import csv
from matplotlib import pyplot as plt


class Data:
    """
    get data from neteasy
    """
    def __init__(self, code = '1399300'):
        url_template = """http://quotes.money.163.com/service/chddata.html?code=%s&start=10071105&end=20160204&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"""
        url = url_template%(code)
        self.lines = requests.get(url).content.decode('gbk').splitlines()

    
    def daily_price(self):
        """
        dump daily price
        """
        ret = []
        for line in self.lines[1:]:
            line = line.rstrip().split(',')
            date = datetime.date(*list(map(int, line[0].split('-'))))
            close = float(line[3])
            ret.append([date, close])
        ret = sorted(ret)
        return ret

def get_week_sample(data, history = 15):
    '''get week sample from daily data'''
    last_days = {}
    prices = {}
    for i in range(len(data)):
        k, v = data[i]
        week = k.isocalendar()[:2]
        last_days[week] = k
        prices[k] = v
    last_days = sorted(last_days.values())
    day_index = {k:i for i, k in enumerate(last_days)}
    
    xs = []
    ys = []
    for i in range(len(data)):
        k, v = data[i]

        if k not in day_index :
            continue

        d_ind = day_index[k]
        y = None
        if d_ind + 1 < len(last_days):
            y = (prices[last_days[d_ind + 1]] 
                    / prices[last_days[d_ind]])
        if y is not None : y = math.log10(y)

        x = data[max(0, i - history) : i + 1]
        if not x : continue

        xs.append(x)
        ys.append(y)
    return xs, ys

def merge_week(*data):
    ws = set()
    for i, d in enumerate(data):
        s = set(x[-1][0] for x in d[0])
        if i == 0 :
            ws = s
        else:
            ws &= s

    rets = []
    for x, y in data:
        data = [[a, b] for a, b in zip(x, y) if a[-1][0] in ws]
        rets.append(list(zip(*data)))
    return rets

        
def group_week(data):
    weeks = {}
    for k, v in data :
        week = k.isocalendar()[:2]
        if week not in weeks : weeks[week] = []
        weeks[week].append([k, v])
    return sorted([(v[0][0], v) for k, v in weeks.items()])

def gen_week_sample(data, history = 20):
    s = []
    for i in range(history + 1, len(data)):
        x = data[i - history:i]
        y = math.log10(data[i][-1][-1][-1]) - math.log10(data[i - 1][-1][-1][-1])
        s.append([x, y])
    return s

def filter_week(*data):
    rets = []
    ws = set()
    for i, d in enumerate(data):
        s = set([x[-1][0] for x, _ in d])
        if i == 0 :
            ws = s
        else:
            ws &= s
    for i, d in enumerate(data):
        d = [[x, y] for x, y in d if x[-1][0] in ws]
        rets.append(d)
    return rets

def sig_m(x):
    cs = [v for _, v in x]
    m = sum(cs) / len(cs)
    return math.log10(x[-1][1]) - math.log10(m)

def sig_t(x):
    total_c = math.log10(x[-1][1]) - math.log10(x[0][1])
    return total_c
def sig_lr(x):
    #cs = [v for _, v in x][:-1]
    cs = [v for _, v in x][:-1]

    cs = [math.log10(x) - math.log10(cs[0]) for x in cs]
    
    cs = np.array(cs)
    xs = np.array(range(len(cs)))
    conf = np.ones(len(xs))
    #for i in range(len(cs) - 2, -1, -1):
        #conf[i] = conf[i + 1] * 0.93
    for i in range(len(cs)):
            cs[len(cs) - 1 - i] *= (i + 1) / (i + 2)
    A = np.vstack([xs, conf]).T
    m, c = np.linalg.lstsq(A, cs)[0]
    return m

def week_t(x):
    total_c = math.log10(x[-1][1][-1][-1]) - math.log10(x[0][1][0][-1])
    return total_c

def week_m(x):
    cs = []
    for _, w in x:
        for _, d in w :
            cs.append(d)
    m = sum(cs) / len(cs)
    return math.log10(x[-1][1][-1][-1]) - math.log10(m)

def week_d(x):
    cs = []
    for _, w in x:
        for _, d in w :
            cs.append(d)
    cs = np.array(cs)
    return math.log10(np.std(cs)) - math.log10(np.mean(cs))

def week_lr(x):
    cs = []
    for _, w in x:
        for _, d in w :
            cs.append(d)
    cs = [math.log10(x) - math.log10(cs[0]) for x in cs]
    #cs = cs[:min(15, len(cs))]
    
    cs = np.array(cs)
    #print(len(cs))
    xs = np.array(range(len(cs)))
    #conf = (xs * 0.15 + 1) / (len(xs) + 1)
    conf = np.ones(len(xs))
    #for i in range(len(cs) - 2, -1, -1):
    #    conf[i] = conf[i + 1] * 0.93
    #print(conf[0])
    A = np.vstack([xs, conf]).T
    #A = np.vstack([xs, conf]).T
    #return np.log10(np.linalg.lstsq(A, cs)[1][0])
    m, c = np.linalg.lstsq(A, cs)[0]
    return m

def multisim2(w_datas, predictor):
    baselines = [[] for i in range(len(w_datas))]
    basey = [0 for i in range(len(w_datas))]
    active =[]
    activey = 0

    for i in range(len(w_datas[0][0])):
        for j in range(len(w_datas)):
            if w_datas[j][1][i] is not None :
                basey[j] += w_datas[j][1][i]
                baselines[j].append([w_datas[j][0][i][-1][0], basey[j]])
            
        pres = [predictor(wd[0][i]) for wd in w_datas]
        max_p = pres[0]
        max_ind = 0
        for j in range(1, len(pres)):
            if pres[j] > max_p :
                max_p = pres[j]
                max_ind = j
                
        if max_p > 0 :
            if w_datas[max_ind][1][i] is not None :
                activey += w_datas[max_ind][1][i]
                active.append([w_datas[j][0][i][-1][0], activey])
        else:
            pass

    for baseline in baselines:
        plt.plot(*(zip(*baseline)))
    plt.plot(*(zip(*active)))
    plt.grid()

def dailysim(data, predictor, history = 20):
    baseline = []
    basey = 0
    active = []
    activey = 0
    for i in range(history, len(data) - 1):
        y = math.log10(data[i + 1][1] / data[i][1])
        baseline.append([data[i][0], basey])
        basey += y
        if predictor(data[i - history:i]) > 0:
            active.append([data[i][0], activey])
            activey += y

    pass
    plt.plot(*(zip(*baseline)))
    plt.plot(*(zip(*active)))
    plt.grid()
    
def multisim(w_datas, predictor):
    baselines = [[] for i in range(len(w_datas))]
    basey = [0 for i in range(len(w_datas))]
    active =[]
    activey = 0
    for i in range(len(w_datas[0])):
        for j in range(len(w_datas)):
            basey[j] += w_datas[j][i][1]
            baselines[j].append([w_datas[j][i][0][-1][0], basey[j]])
            
        pres = [predictor(wd[i][0]) for wd in w_datas]
        max_p = pres[0]
        max_ind = 0
        for j in range(1, len(pres)):
            if pres[j] > max_p :
                max_p = pres[j]
                max_ind = j
                
        if max_p > 0 :
            activey += w_datas[max_ind][i][1]
            active.append([w_datas[j][i][0][-1][0], activey])
        else:
            pass

    for baseline in baselines:
        plt.plot(*(zip(*baseline)))
    plt.plot(*(zip(*active)))
    plt.grid()
        
"""
def sim(w_data, predictor):
    baseline = []
    basey = 1
    active =[]
    activey = 1
    for x, y in w_data:
        basey += y
        baseline.append([x[-1][0], basey])
        
        if predictor(x) > 0:
            activey += y
            active.append([x[-1][0], activey])
            pass
        else:
            pass
        
    plt.plot(*(zip(*baseline)))
    plt.plot(*(zip(*active)))
    plt.grid()
"""
