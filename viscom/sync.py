import datetime, time
from dateutil.relativedelta import relativedelta
import ctypes, sys, os
import ntplib
import win32api
import http.client

def CurrentTime():
    dat, tm = syncTime()
    c = ntplib.NTPClient()
    print (dat[7:])
    print (tm[5:])
    datetime_ = time.strptime(dat[7:] + " " + tm[5:], '%y-%m-%d %H:%M:%S')
    print (datetime_)
    # response = c.request("pool.ntp.org")
    # ts = response.tx_time
    #
    # _time = datetime.datetime.fromtimestamp(response.tx_time, datetime.timezone.utc)
    # print (_time)
    # return _time
    return datetime_

# def SyncTime():
#     ''' don't know why this's not working'''
#     c = ntplib.NTPClient()
#     response = c.request("pool.ntp.org")
#     ts = response.tx_time
#     _date = time.strftime("%m-%d-%y", time.localtime(ts))
#     print ("date {}".format(_date))
#     os.system("date {}".format(_date))
#     os.system("time {}".format((datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%H:%M:%S')))
#     print("Note: System time is rolled back to the local time.")

def syncTime(url = "www.baidu.com"):
    conn = http.client.HTTPConnection(url)
    conn.request("GET", "/")
    r = conn.getresponse()
    # r.getheaders() #获取所有的http头
    ts = r.getheader('date')  # 获取http头date部分
    # 将GMT时间转换成北京时间
    ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")  # 格式ts
    ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)  # +东八区
    dat = "date %u-%02u-%02u" % (ttime.tm_year, ttime.tm_mon, ttime.tm_mday)
    tm = "time %02u:%02u:%02u" % (ttime.tm_hour, ttime.tm_min, ttime.tm_sec)
    os.system(dat)
    os.system(tm)
    print("Note: System time is rolled back to the local time.")
    return [dat, tm]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def RollBackTime():
    syncTime()
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    license_time = datetime.datetime.now() + relativedelta(years=-13)
    win32api.SetLocalTime(license_time)
    print ("Note: System time is changed to validate the Vissim certificate.")

if __name__ == "__main__":
    RollBackTime()
    dt = syncTime()