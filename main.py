from config import InitVissim, SyncTime
from tests import test
from viscom.simulation import *

def _trial1():
    vis = InitVissim()
    SyncTime()
    # test.test_create_networks()
    vis.LoadNet(r'C:\Users\mini_lab\PycharmProjects\\vis_project_p_may_05_21_01\\networks\example\\test1.inp')
    sim = vis.Simulation
    net = vis.Net
    eval = vis.Evaluation
    print(dir(sim))
    print(dir(net))
    print(dir(eval))

if __name__ == "__main__":
    dir = r'C:\Users\mini_lab\PycharmProjects\\vis_project_p_may_05_21_01\\networks\example\\test_f001.inp'
    vis = OpenVissim(dir)
    vis.runSimulation(_totalPeriod = 600)


