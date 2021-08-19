import numpy as np

'''
    use the following matrix to dynamically update volume on each link
    label = {"volume", "timefrom", "timeuntil", "inputID", "composition"}
'''
_flowMatrix = np.asarray([
    [5000, 0, 50, 1, 2],
    [5000, 50, 100, 2, 2],
    [15000, 100, 200, 3, 2],
    [15000, 200, 300, 4, 2],
    [5000, 300, 400, 5, 2],
    [5000, 400, 450, 6, 2],
    [5000, 450, 1800, 7, 2],
    [2000, 0, 50, 16, 2],
    [2000, 0, 50, 17, 2],
    [8000, 0, 50, 18, 2],
    [8000, 50, 100, 19, 2],
    [2000, 50, 100, 20, 2],
    [2000, 50, 100, 21, 2],
    [2000, 100, 150, 22, 2],
    [8000, 100, 150, 23, 2],
    [2000, 100, 150, 24, 2]
])

_flowMatrix2 = np.asarray([
    [5000, 0, 600, 2, 2],
    [25000, 0, 600, 1, 2]
])

'''
    use the following matrix to control lane closure on each link
    label = {"fromtime", "untiltime", "link", "lane", "class"}
'''
_lcMatrix = np.asarray([
    [0, 300, 4, 3, 10],
    [0, 300, 4, 4, 10],
    [0, 300, 4, 5, 10]
])

_lcMatrix2 = np.asarray([
    [0, 250, 1, 1, 10],
    [0, 250, 1, 2, 10],
    [0, 250, 1, 3, 10]
])


class FlowAdjust:
    def __init__(self, flowMatrix = _flowMatrix2, lcMatrix = _lcMatrix2):
        self.para = flowMatrix
        self.lcAdjustor = lcMatrix
