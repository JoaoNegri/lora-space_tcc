import random
import numpy as np
from aux import airtime

class Packet():
    
    C = 299792.458 ###SPEED LIGHT [km/s]
    
    def __init__(self, nodeid:int, packetlen:int, dist: np.ndarray[int, np.float64], Ptx: int,
                  Prx: np.ndarray[int, np.float64], frequency: list[int], distance: np.ndarray[int, np.float64]):
        self.nodeid = nodeid
        self.txpow = Ptx
        self.sf = 12
        self.cr = 1 ##CODING RATE
        self.bw = 125
        self.pl = packetlen

        self.transRange = 150
        self.symTime = (2.0**self.sf)/self.bw
        self.arriveTime = 0
        self.freq = int(random.choice(frequency)) 
        self.rectime = airtime(self.sf,self.cr,self.pl,self.bw) ##RECTIME IS THE RECEPTION TIME (ie AIRTIME)


        self.proptime = distance[nodeid%len(distance),:,:]*(1/Packet.C)
        self.collided = 0
        self.processed = 0
        self.lost = bool