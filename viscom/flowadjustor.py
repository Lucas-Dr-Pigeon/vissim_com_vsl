import numpy as np

'''
    use the following matrix to dynamically update volume on each link
    label = {"volume", "timefrom", "timeuntil", "inputID", "composition"}
'''
_flowMatrix = np.asarray([
    [6000, 0, 100, 1, 2],
    [6000, 100, 300, 2, 2],
    [6000, 300, 1800, 3, 2]
])
'''
    use the following matrix to control lane closure on each link
    label = {"fromtime", "untiltime", "link", "lane", "class"}
'''
_lcMatrix = np.asarray([
    [0, 0, 4, 3, 10],
    [0, 0, 4, 4, 10],
    [0, 0, 4, 5, 10]
])


class FlowAdjust:
    def __init__(self, flowMatrix = _flowMatrix, lcMatrix = _lcMatrix):
        self.para = flowMatrix
        self.lcAdjustor = lcMatrix
