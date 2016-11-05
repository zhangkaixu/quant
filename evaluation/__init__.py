from __future__ import print_function
from pylab import *

def yearly_sharpe(pnl):
    return np.mean(pnl) / np.std(pnl) * np.sqrt(252)

def max_drawdown(pnl):
    peak_value = None
    peak_idx = -1
    max_dd = 0
    value = 1.
    for i in range(len(pnl)):
        value += pnl[i]
        if peak_idx == -1 or value > peak_value:
            peak_idx = i
            peak_value = value
        dd = (peak_value - value) / peak_value
        if dd > max_dd :
            max_dd = dd
    return max_dd

def longest_drawdown(pnl):
    peak_value = None
    peak_idx = -1
    l_dd = 0
    value = 1.
    for i in range(len(pnl)):
        value += pnl[i]
        if peak_idx == -1 or value > peak_value:
            peak_idx = i
            peak_value = value
        dd = (peak_value - value) / peak_value
        if i - peak_idx > l_dd:
            l_dd = i - peak_idx
    return l_dd

