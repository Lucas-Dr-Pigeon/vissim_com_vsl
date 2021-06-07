import win32com.client as com
import viscom.sync as sync
import pandas as pd
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
from viscom.flowadjustor import *
import numpy as np
import random as rd
import time

class OpenVissim:
    def __init__(self, dir, ver = 430):
        sync.RollBackTime()
        dispatch = "Vissim.Vissim." + str(ver)
        print("Connecting to VISSIM&COM service ...")
        self.Vissim = com.Dispatch(dispatch)
        sync.SyncTime()
        print("Loading network file ...")
        self.Vissim.LoadNet(dir)
        self.trajectory = []
        self.flowAdjustor = None
        self.lcAdjustor = None
        self.timesAdjust = None
        self.timesLC = None
        self.totalPeriod = -1
        self.resolution = -1
        self.exportFile = None

    def runSimulation(self, _totalPeriod = 10, _resolution = 10):
        print("Initializing simulation ...")
        self.totalPeriod = _totalPeriod
        self.resolution = _resolution
        self.Vissim.Simulation.Period = _totalPeriod
        self.Vissim.Simulation.Resolution = _resolution
        self.Vissim.Evaluation.SetAttValue("vehiclerecord", True)
        self.Vissim.Evaluation.SetAttValue("datacollection", True)
        # self.Vissim.Net.Links.GetLinkByNumber(1).SetAttValue2("LANECLOSED", 2, 10, True)
        self.flowAdjustor = FlowAdjust().para
        self.lcAdjustor = FlowAdjust().lcAdjustor
        self.loadFlowAdjustor()

        for _step in range(0, _totalPeriod * _resolution):
            # self.adjustFlow(_step)
            print("Running step " + str(_step) + "/" + str(self.totalPeriod * self.resolution))
            if _step in self.timesAdjust * self.resolution:
                _volume = self.flowAdjustor[np.where(self.timesAdjust * self.resolution == _step)[0][0]][0]
                print("Traffic volume on link" + str("?") + " has changed to " + str(_volume) + " at frame #" + str(_step), end="\r" )
            self.laneClose(_step)
            self.Vissim.Simulation.RunSingleStep()
            self.collectData(_step)
        self.stopSimulation()
        self.exportData()
        self.plotDiagram()

    def loadFlowAdjustor(self):
        Num = self.flowAdjustor.shape[0]
        self.timesAdjust = self.flowAdjustor[:, 1]
        for _idx in range(Num):
            _volume = self.flowAdjustor[_idx][0]
            _timefrom = self.flowAdjustor[_idx][1]
            _timeuntil = self.flowAdjustor[_idx][2]
            _inputID = self.flowAdjustor[_idx][3]
            _comp = self.flowAdjustor[_idx][4]
            vehin = self.Vissim.Net.VehicleInputs.GetVehicleInputByNumber(_inputID)
            vehin.SetAttValue("TIMEFROM", _timefrom)
            vehin.SetAttValue("TIMEUNTIL", _timeuntil)
            # vehin.SetAttValue("TRAFFICCOMPOSITION", _comp)
            vehin.SetAttValue("VOLUME", _volume)

    def adjustFlow(self, _step):
        TimeFroms = self.flowAdjustor[:,1] * self.resolution
        if _step in TimeFroms:
            _idx = int(np.where(TimeFroms == _step)[0][0])
            _inputID = int(self.flowAdjustor[_idx][3])
            _comp = int(self.flowAdjustor[_idx][4])
            _volume = int(self.flowAdjustor[_idx][0])
            _timefrom = int(self.flowAdjustor[_idx][1])
            _timeuntil = int(self.flowAdjustor[_idx][2])
            vehin = self.Vissim.Net.VehicleInputs.GetVehicleInputByNumber(_inputID)
            # _link = vehin.AttValue("LINK")
            vehin.SetAttValue("TIMEUNTIL", _timeuntil)
            vehin.SetAttValue("TIMEFROM", _timefrom)
            vehin.SetAttValue("VOLUME", _volume)
            # vehin.SetAttValue("TRAFFICCOMPOSITION", _comp)
            print(
                "Traffic volume on link" + str("?") + " has changed to " + str(_volume) + " at frame #" + str(_step)
            )




    def laneClose(self, _step):
        global _linkid, _lane, _class
        for _idx, _row in enumerate(self.lcAdjustor):
            _linkid = int(_row[2])
            _lane = int(_row[3])
            _class = int(_row[4])
            if _row[0] * self.resolution == _step:
                print("At frame #" + str(_step) + ", lane #" + str(_lane) + " was closed.")
                self.Vissim.Net.Links.GetLinkByNumber(_linkid).SetAttValue2("LANECLOSED", _lane, _class, True)
            if _row[1] * self.resolution == _step:
                print("At frame #" + str(_step) + ", lane #" + str(_lane) + " was reopened.")
                self.Vissim.Net.Links.GetLinkByNumber(_linkid).SetAttValue2("LANECLOSED", _lane, _class, False)
            # _lcAtt = self.Vissim.Net.Links.GetLinkByNumber(_linkid).AttValue2("LANECLOSED", 3, 10)
            # print ("Status: " + str(_lcAtt))


    def stopSimulation(self):
        self.Vissim.Simulation.Stop()
        print("Simulation complete.")

    def collectData(self, _step):
        for link in self.Vissim.Net.Links:
            for _veh in link.GetVehicles():
                try:
                    _id = _veh.AttValue("ID")
                except:
                    _id = "?"
                    print ("Failed to retrieve vehicle id!")
                try:
                    _name = _veh.AttValue("Name")
                except:
                    _name = "?"
                    print ("Failed to retrieve vehicle name!")
                try:
                    _link = _veh.AttValue("LINK")
                except:
                    _link = "?"
                    print ("Failed to retrieve vehicle's link!")
                try:
                    _coord = _veh.AttValue("LINKCOORD")
                except:
                    _coord = "?"
                    print ("Failed to retrieve vehicle's location on link!")
                try:
                    _speed = _veh.AttValue("SPEED")
                except:
                    _speed = "?"
                    print ("Failed to retrieve vehicle's speed!")
                try:
                    _desSpeed = _veh.AttValue("DESIREDSPEED")
                except:
                    _desSpeed = "?"
                    print ("Failed to retrieve vehicle's desired speed!")
                try:
                    _lane = _veh.AttValue("LANE")
                except:
                    _lane = "?"
                    print ("Failed to retrieve vehicle's lane!")

                _row = [_step, _id, _name, _link, _coord, _lane, _speed, _desSpeed]
                self.trajectory.append(_row)

    def exportData(self, _folder = "./results/"):
        now = datetime.now()
        dir = _folder + now.strftime("%b-%d-%Y-%H-%M-%S") + ".csv"
        _labels = ["frame", "id", "name", "link", "coord", "lane", "speed", "desired_speed"]
        df = pd.DataFrame(self.trajectory, columns = _labels)
        df.to_csv(dir)
        self.exportFile = dir
        print("Saving file to " + str(self.exportFile))
        self.plotTrajectory()

    def plotTrajectory(self, _link = 3, _lane = 3):
        print("Generating x-t diagram of link #" + str(_link) + " lane #" + str(_lane) + " ...")
        df = pd.read_csv(self.exportFile)
        df_select = df[(df["link"] == _link) & (df["lane"] == _lane)]
        Vehicles = df_select["id"].unique()
        for _veh in Vehicles:
            df_veh = df_select[df_select["id"] == _veh]
            df_veh.sort_values("frame", ascending = True)
            series_x = df_veh["coord"].to_list()
            series_t = df_veh["frame"].to_list()
            plt.plot(series_t, series_x, color = "black")
        plt.xlabel("time")
        plt.ylabel("distance")
        plt.show()

    def plotDiagram(self, _samples=200, _dx=200, _dt=100, _lane=3, _link=3, _thres=-1):
        print("Generating Q-K diagram ...")
        totalLength = self.Vissim.Net.Links.GetLinkByNumber(_link).AttValue("LENGTH")
        totalPeriod = self.totalPeriod
        df = pd.read_csv(self.exportFile)
        Densities = {"FREE": [], "CONGEST": []}
        Flows = {"FREE": [], "CONGEST": []}
        Speeds = {"FREE": [], "CONGEST": []}
        while len(Flows["FREE"]) + len(Flows["CONGEST"]) < 200:
            x1 = 0 + rd.random() * (totalLength - _dx - 0)
            x2 = x1 + _dx
            t1 = 0 + rd.random() * (totalPeriod - _dt - 0)
            t2 = t1 + _dt
            ''' find trajectories corresponding to the designated X-T zone '''
            Trj = df[ (df['coord'] < x2)     &
                      (df['coord'] >= x1)    &
                      (df['frame'] < t2)     &
                      (df['frame'] >= t1)    &
                      (df['lane'] == _lane)  &
                      (df['link'] == _link)  ]
            flow, dens, speed = self.getElements(Trj, _dx, _dt)
            if speed == -1:
                continue
            if dens < 60 or _thres <= 0:
                if _thres > 0 and len(Flows["FREE"]) >= _samples / 2:
                    continue
                Flows["FREE"].append(flow)
                Densities["FREE"].append(dens)
                Speeds["FREE"].append(speed)
            elif dens >= 60:
                if len(Flows["CONGEST"]) >= _samples / 2:
                    continue
                Flows["CONGEST"].append(flow)
                Densities["CONGEST"].append(dens)
                Speeds["CONGEST"].append(speed)
        plt.scatter(Densities["FREE"], Flows["FREE"], color="blue", s=0.5)
        plt.scatter(Densities["CONGEST"], Flows["CONGEST"], color="red", s=0.5)
        plt.show()

    def getElements(self, _Trj, _dx=200, _dt=100):
        _dx /= 1000
        _dt /= 36000
        ''' find all unique vehicles in the designated X-T zone '''
        Vehicles = np.asarray(sorted(set(_Trj['id'])))
        dx = _Trj.groupby('id')['coord'].max() - _Trj.groupby('id')['coord'].min()
        dt = _Trj.groupby('id')['frame'].max() - _Trj.groupby('id')['frame'].min() + 1
        dxSum = dx.sum(axis=0) / 1000
        dtSum = dt.sum(axis=0) / 10 / 3600
        flow, dens = dxSum / _dx / _dt, dtSum / _dx / _dt
        if flow + dens == 0:
            speed = -1
        else:
            speed = flow / dens
        return flow, dens, speed




if __name__ == "__main__":

    def plotTrajectory(_dir, _link = 3, _lane = 3):
        df = pd.read_csv(_dir)
        df_select = df[(df["link"] == _link) & (df["lane"] == _lane)]
        Vehicles = df_select["id"].unique()
        for _veh in Vehicles:
            df_veh = df_select[df_select["id"] == _veh]
            df_veh.sort_values("frame", ascending = True)
            series_x = df_veh["coord"].to_list()
            series_t = df_veh["frame"].to_list()
            plt.plot(series_t, series_x, color = "black")
        plt.xlabel("time")
        plt.ylabel("distance")
        plt.show()

    def plotDiagram(_dir, _samples=200, _dx=200, _dt=100, _lane = 1, _link = 2, _thres=-1):
        totalLength = 800
        totalPeriod = 180 * 10
        df = pd.read_csv(_dir)
        Densities = {"FREE": [], "CONGEST": []}
        Flows = {"FREE": [], "CONGEST": []}
        Speeds = {"FREE": [], "CONGEST": []}
        while len(Flows["FREE"]) + len(Flows["CONGEST"]) < 200:
            x1 = 0 + rd.random() * (totalLength - _dx - 0)
            x2 = x1 + _dx
            t1 = 0 + rd.random() * (totalPeriod - _dt - 0)
            t2 = t1 + _dt
            ''' find trajectories corresponding to the designated X-T zone '''
            Trj = df[ (df['coord'] < x2)     &
                      (df['coord'] >= x1)    &
                      (df['frame'] < t2)     &
                      (df['frame'] >= t1)    &
                      (df['lane'] == _lane)  &
                      (df['link'] == _link)  ]
            flow, dens, speed = getElements(Trj, _dx, _dt)
            if speed == -1:
                continue
            if dens < 60 or _thres <= 0:
                if _thres > 0 and len(Flows["FREE"]) >= _samples / 2:
                    continue
                Flows["FREE"].append(flow)
                Densities["FREE"].append(dens)
                Speeds["FREE"].append(speed)
            elif dens >= 60:
                if len(Flows["CONGEST"]) >= _samples / 2:
                    continue
                Flows["CONGEST"].append(flow)
                Densities["CONGEST"].append(dens)
                Speeds["CONGEST"].append(speed)
        plt.scatter(Densities["FREE"], Flows["FREE"], color = "blue", s = 0.5)
        plt.scatter(Densities["CONGEST"], Flows["CONGEST"], color="red", s=0.5)
        plt.show()



    def getElements(_Trj, _dx = 200, _dt = 100):
        _dx /= 1000
        _dt /= 36000
        ''' find all unique vehicles in the designated X-T zone '''
        Vehicles = np.asarray(sorted(set(_Trj['id'])))
        dx = _Trj.groupby('id')['coord'].max() - _Trj.groupby('id')['coord'].min()
        dt = _Trj.groupby('id')['frame'].max() - _Trj.groupby('id')['frame'].min() + 1
        dxSum = dx.sum(axis = 0) / 1000
        dtSum = dt.sum(axis = 0) / 10 / 3600
        flow, dens = dxSum / _dx / _dt, dtSum / _dx / _dt
        if flow + dens == 0:
            speed = -1
        else:
            speed = flow / dens
        return flow, dens, speed




    plotTrajectory(_dir = r"C:\Users\mini_lab\PycharmProjects\vis_project_p_may_05_21_01\results\May-22-2021-14-57-56.csv")
    plotDiagram(_dir = r"C:\Users\mini_lab\PycharmProjects\vis_project_p_may_05_21_01\results\May-22-2021-11-09-40.csv")
