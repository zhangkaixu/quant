import math
import requests
import datetime

class Data:
    def __init__(self, code = '1399300'):
        url_template = """http://quotes.money.163.com/service/chddata.html?code=%s&start=10071105&end=20160204&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"""
        url = url_template%(code)
        self.lines = requests.get(url).content.decode('gbk').splitlines()

    def daily_price(self):
        ret = []
        for line in self.lines[1:]:
            line = line.rstrip().split(',')
            date = datetime.date(*list(map(int, line[0].split('-'))))
            close = float(line[3])
            ret.append([date, close])
        ret = sorted(ret)
        return ret

        
def group_week(data):
    weeks = {}
    for k, v in data :
        week = k.isocalendar()[:2]
        if week not in weeks : weeks[week] = []
        weeks[week].append([k, v])
    return sorted([(v[0][0], v) for k, v in weeks.items()])

def gen_week_sample(data):
    history = 4
    s = []
    for i in range(history + 1, len(data)):
        x = data[i - history:i]
        y = math.log10(data[i][-1][-1][-1]) - math.log10(data[i - 1][-1][-1][-1])
        s.append([x, y])
    return s
