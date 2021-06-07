import datetime, time
from dateutil.relativedelta import relativedelta
import ctypes, sys, os
import ntplib
import win32api

def CurrentTime():
    c = ntplib.NTPClient()
    response = c.request("pool.ntp.org")
    ts = response.tx_time
    _time = datetime.datetime.fromtimestamp(response.tx_time, datetime.timezone.utc)
    return _time

def SyncTime():
    c = ntplib.NTPClient()
    response = c.request("pool.ntp.org")
    ts = response.tx_time
    _date = time.strftime("%m-%d-%y", time.localtime(ts))
    print (_date)
    os.system("date {}".format(_date))
    os.system("time {}".format((datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%H:%M:%S')))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def RollBackTime():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    license_time = CurrentTime() + relativedelta(years=-13)
    win32api.SetLocalTime(license_time)