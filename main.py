from config import InitVissim, SyncTime
from tests import test
from viscom.simulation import *

def _trial1():
    vis = InitVissim()
    SyncTime()
    # test.test_create_networks()
    vis.LoadNet(r'C:\Users\Lucas_Pigeon\PythonProjects\\vissim_com_vsl\\networks\example\\test1.inp')
    sim = vis.Simulation
    net = vis.Net
    eval = vis.Evaluation
    print(dir(sim))
    print(dir(net))
    print(dir(eval))

if __name__ == "__main__":
    dir = r'C:\Users\Pigeon_Zuo\PythonProjects\\vissim_com_vsl\\networks\example\\test3_ramps.inp'

    vis = OpenVissim(dir)
    vis.runSimulation(_totalPeriod=300)




