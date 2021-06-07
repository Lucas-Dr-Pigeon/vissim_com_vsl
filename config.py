import re
import datetime, time
import win32com.client as com
import win32api
from dateutil.relativedelta import relativedelta
import ctypes, sys, os
import ntplib

def _readSection(self, line):
    """ Process the Input section of the INP file.
    """
    if re.match('^INPUT\s+\d+', line):
        inputNum = self.types['input'](re.findall('INPUT\s+(\d+)', line)[0])
        self.currData = {'input': inputNum}
    elif re.match('^\s+NAME', line):
        self.currData['name'] = re.findall('NAME\s+(".+"|"")', line)[0]
        self.currData['label'] = re.findall('LABEL\s+(-?\d+.\d+)\s(-?\d+.\d+)', line)[0]
    elif re.match('^\s+LINK', line):
        self.currData['link'] = re.findall('LINK\s+(\d+)', line)[0]
        if re.search('EXACT', line):
            self.currData['exact'] = True
            self.currData['q'] = re.findall('Q EXACT (.+) COMPOSITION',
                                          line)[0]
        else:
            self.currData['exact'] = False
            self.currData['q'] = re.findall('Q (.+) COMPOSITION', line)[0]
        self.currData['composition'] = re.findall('COMPOSITION (\d)',
                                                line)[0]
    elif re.match('^\s+TIME', line):
        self.currData['from'] = re.findall('FROM (\d+.\d+)', line)[0]
        self.currData['until'] = re.findall('UNTIL (\d+.\d+)', line)[0]
        # Last line, create Input object
        self.create(self.currData['link'], self.currData['q'],
                    self.currData['composition'], **self.currData)
    else:
        print
        'Non-Input data provided: %s' % line


def _importSection(obj, filename):
    """ Imports section's syntax into dictionary.
    """
    name = obj.name
    try:
        with open(filename, 'r') as data:
            section = None
            for row in data:
                found = re.findall(r'(?<=\- )(.*?)(?=\: -)', row)
                if row in ['\n', '\r\n']:
                    continue
                elif found:
                    section = found[0]
                elif section == name and row[0] != '-':
                    obj._readSection(row)
                else:
                    continue
    except IOError:
        print ('cannot open', filename)

def _checkKeyData(obj, key, label):
    """ Checks whether key and label exist
    """
    if key is not None:
        if key not in obj.data:
            raise KeyError('%s not a valid key for object %s' %
                           (key, obj.name))
    if label not in obj.types:
        raise KeyError('%s not a valid label for object %s' %
                       (label, obj.name))
    return True

def _getData(obj, key, label):
    """ Returns requested value from vissim object
    """
    _checkKeyData(obj, key, label)
    if key is None:
        new = obj.data[label]
    else:
        new = obj.data[key][label]
    return re.copy(new)

def _setData(obj, key, label, value):
    """ Sets given value in vissim object
    """
    _checkKeyData(obj, key, label)
    if not isinstance(value, obj.types[label]):
        value = obj.types[label](value)
    if key is None:
        obj.data[label] = value
    else:
        obj.data[key][label] = value


def _updateData(obj, key, label, value, pos=None, newKey=None):
    """ Updates vissim object
        Input: object, key, label and value
        Output: adds value to object.
    """
    _checkKeyData(obj, key, label)
    if key is None:
        if (isinstance(obj.data[label], list) is True) and (pos is None):
            obj.data[label].append(value)
            obj.data[label] = list(_flatten(obj.data[label]))
        elif isinstance(obj.data[label], list) and pos:
            obj.data[label].insert(pos, value)
            obj.data[label] = list(_flatten(obj.data[label]))
    else:
        if isinstance(obj.data[key][label], dict):
            obj.data[key][label][newKey] = value
        if (isinstance(obj.data[key][label], list) is True) and (pos is None):
            obj.data[label].append(value)
            obj.data[label] = list(_flatten(obj.data[label]))
        elif isinstance(obj.data[key][label], list) and pos:
            obj.data[label].insert(pos, value)
            obj.data[label] = list(_flatten(obj.data[label]))

def _flatten(coll):
    """ Flatten list and convert elements to int
    """
    if isinstance(coll, list):
        return [int(a) for i in coll for a in _flatten(i)]
    else:
        return [coll]

class Links:
    '''
    Handles Links section of .INP file.
    '''

    def __init__(self, filename):
        self.filename = filename
        self.name = 'Links'
        self.data = {}
        self.over = None
        self.currData = None
        self.closed = None
        self.types = {"link": int, "name": str, "label": tuple, "behaviortype": int,
                      "displaytype": int, "length": float, "lanes": int, "lane_width": list, "gradient": float,
                      "cost": float, "surchargers": list, "segment_length": float, "evaluation": bool,
                      "from": list, "over": list, "to": list, "closed": dict}
        _importSection(self, filename)

    def get(self, linkNum, label, string=True):
        """ Get value from Link.
            Input: Link number, Value label
            Output: Value
        """
        if string:
            return str(_getData(self, linkNum, label))
        else:
            return _getData(self, linkNum, label)

    def set(self, linkNum, label, value):
        """ Set value from Link.
            Input: Link number, value label, value
            Output: Change is made in place
        """
        _setData(self, linkNum, label, value)

    def getInputNumByLink(self, linkNum):
        """ Get value from Input by link number
            Input: Link number
            Output: List of input numbers
        """
        result = [k for k, v in self.data.items() if v['link'] == linkNum]
        if len(result) == 0:
            raise KeyError('%s not in data' % (linkNum))
        else:
            return result

    def create(self, linkNum, demand, comp, **kwargs):
        """ Create new Input
            Input: link number, demand, vehicle composition
            Output: Creates Input object
        """
        if self.data.keys():
            num = max(self.data.keys()) + 1
        else:
            num = 1
        inputNum = kwargs.get('input', num)
        self.set(inputNum, 'input', inputNum)
        self.set(inputNum, 'q', demand)
        self.set(inputNum, 'link', linkNum)
        self.set(inputNum, 'composition', comp)

        self.set(inputNum, 'name', kwargs.get('name', '""'))
        self.set(inputNum, 'label', kwargs.get('label', ('0.00', '0.00')))
        self.set(inputNum, 'from', kwargs.get('from', '0.0'))
        self.set(inputNum, 'until', kwargs.get('until', '3600.0'))
        self.set(inputNum, 'exact', kwargs.get('exact', False))

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

def InitVissim(modify_time = True):
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    if modify_time:
        license_time = CurrentTime() + relativedelta(years=-13)
        win32api.SetLocalTime(license_time)
    print("Connecting to Vissim")
    vis = com.Dispatch("Vissim.Vissim.430")
    return vis

if __name__ == "__main__":
    vis = InitVissim()



     

