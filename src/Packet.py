import random
import numpy as np
from aux import airtime

class Packet():
    def __init__(self, nodeid:int, packetlen:int, dist: np.ndarray[int, np.float64], Ptx: int,
                  Prx: np.ndarray[int, np.float64], frequency: list[int], distance: np.ndarray[int, np.float64]):
        #global experiment
        #global gamma
        #global d0
        #global var
        #global freq
        #global GL
        global channel
        #SF = [7,8,9,10,11,12]
        self.nodeid = nodeid
        self.txpow = Ptx
        #self.sf = random.choice(SF)
        self.sf = 12
        self.cr = 1 ##CODING RATE
        self.bw = 125
        # transmission range, needs update XXX
        self.transRange = 150
        self.pl = packetlen
        self.symTime = (2.0**self.sf)/self.bw
        self.arriveTime = 0
        self.rssi = Prx[nodeid%len(Prx),:,:]
        self.freq = int(random.choice(frequency)) 
        self.rectime = airtime(self.sf,self.cr,self.pl,self.bw) ##RECTIME IS THE RECEPTION TIME (ie AIRTIME)

        c = 299792.458 ###SPEED LIGHT [km/s]

        self.proptime = distance[nodeid%len(distance),:,:]*(1/c)
        #print ("rectime node ", self.nodeid, "  ", self.rectime)
        #print ("Airtime for node {} is {} [seconds]".format(self.nodeid,self.rectime)) #from https://www.loratools.nl/#/airtime
        # denote if packet is collided
        self.collided = 0
        self.processed = 0
        self.lost = bool