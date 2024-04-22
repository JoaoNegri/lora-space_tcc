import random
import numpy as np
from Packet import Packet
from Intrapacket import IntraPacket
from Header import Header

class Node():
    def __init__(self, nodeid:int, bs:int, avgSendTime:int, packetlen:int, 
                 total_data:int, distance: np.ndarray[int,np.float64], 
                 elev: np.ndarray[int, np.float64], channel: list[int], Ptx:int, 
                 Prx: np.ndarray[int, np.float64], frequency: list[int],
                 num_sat: int):

        self.dr = 8
        #carriers = list(range(280))
        #random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
        self.nodeid = nodeid
        self.avgSendTime = avgSendTime
        self.bs = bs
        self.packetlen = packetlen
        self.ch = int(random.choice(channel)) 
        self.packet = Packet(self.nodeid, packetlen, Ptx, Prx, frequency, distance, num_sat)
        #self.freqHop = carriers[0:35]

        self.buffer = []
        self.sent = []
        self.totalLost = []
        self.totalColl = []
        self.totalRec = []
        self.totalProc = []
        for _ in range(num_sat):
            self.buffer.append(total_data)
            self.sent.append(0)
            self.totalLost.append(0) 
            self.totalColl.append(0)
            self.totalRec.append(0)
            self.totalProc.append(0)


        if self.dr == 8:
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            self.freqHop = carriers[0:35]
        elif self.dr == 9:
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            self.freqHop = carriers[0:35]
        elif self.dr == 10:
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            self.freqHop = carriers[0:86]
        elif self.dr == 11:
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            self.freqHop = carriers[0:86]
        
        self.header = Header(self.nodeid,self.ch,self.freqHop, self.dr, Prx, Ptx, distance, num_sat)
        self.intraPacket = IntraPacket(self.nodeid,self.ch,self.freqHop,self.dr, Prx, Ptx, distance, num_sat)