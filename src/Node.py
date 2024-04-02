import random
import numpy as np
from Packet import Packet
from Intrapacket import IntraPacket
from Header import Header

class Node():
    def __init__(self, nodeid, bs, avgSendTime, packetlen, total_data, distance, elev, channel, Ptx, Prx, frequency):
        global DR
        self.dr = 8
        #carriers = list(range(280))
        #random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
        self.nodeid = nodeid
        self.avgSendTime = avgSendTime
        self.bs = bs
        self.dist = distance[nodeid%len(distance),:]
        self.elev = elev[nodeid%len(elev),:]
        self.mindist = np.amin(distance[nodeid%len(distance),:])
        self.mindist_pos = int(np.where(distance[nodeid%len(distance),:] == np.amin(distance[nodeid%len(distance),:]))[0])
        #print('node %d' %nodeid, "dist: ", self.dist[0])
        self.buffer = total_data
        self.packetlen = packetlen
        self.ch = int(random.choice(channel)) 
        self.packet = Packet(self.nodeid, packetlen, self.dist, Ptx, Prx, frequency, distance)
        #self.freqHop = carriers[0:35]
        self.sent = 0 #INITIAL SENT PACKETS
        self.totalLost = 0 #INITIAL TOTAL LOST FOR PARTICULAR NODE
        self.totalColl = 0
        self.totalRec = 0
        self.totalProc = 0
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
        
        self.header = Header(self.nodeid,self.dist,self.ch,self.freqHop, self.dr, Prx, Ptx, distance)
        self.intraPacket = IntraPacket(self.nodeid,self.dist,self.ch,self.freqHop,self.dr, Prx, Ptx, distance)