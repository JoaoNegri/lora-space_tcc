import math
import numpy as np


#definição de variaveis estaticas

ISDR8 = np.array([1,-23,-24,-25])
ISDR9 = np.array([-20,1,-20,-21])
ISDR10 = np.array([-18,-17,1,-17])
ISDR11 = np.array([-15,-14,-13,1])

IsoThresholds = np.array([ISDR8,ISDR9,ISDR10,ISDR11])

def powerCollision_2(p1, p2, env):
    #powerThreshold = 6
    global Collmap
    #print ("SF: node {} has {} ; node {} has {}".format(p1.nodeid,p1.sf, p2.nodeid, p2.sf))
    #print ("pwr: node {} with rssi {} dBm and node {} with rssi {} dBm; diff {:3.2f} dBm".format(p1,p1.rssi[math.ceil(env.now)], p2.nodeid,p2.rssi[math.ceil(env.now)], p1.rssi[math.ceil(env.now)] - p2.rssi[math.ceil(env.now)]))
    if True: #p1.sf == p2.sf:
        if abs(p1.rssi[0][math.ceil(env.now)] - p2.rssi[0][math.ceil(env.now)]) < IsoThresholds[p1.dr-8][p2.dr-8]:
            #TODO VERIFICAR O 0 !!!!!!!!!!!!!!!!!
            print ("collision pwr both node {} and node {}".format(p1.nodeid, p2.nodeid))
            #Collmap[p1.sf-7][p2.sf-7] += 1
            #Collmap[p2.sf-7][p1.sf-7] += 1
            # packets are too close to each other, both collide
            # return both packets as casualties
            return (p1, p2)
        elif p1.rssi[0][math.ceil(env.now)] - p2.rssi[0][math.ceil(env.now)] < IsoThresholds[p1.dr-8][p2.dr-8]:
            #TODO VERIFICAR O 0 !!!!!!!!!!!!!!!!!
            # p2 overpowered p1, return p1 as casualty
            print ("collision pwr node {} overpowered node {}".format(p2.nodeid, p1.nodeid))
            print ("capture - p2 wins, p1 lost")
            #Collmap[p1.sf-7][p2.sf-7] += 1
            return (p1,)
        print ("capture - p1 wins, p2 lost")
        # p2 was the weaker packet, return it as a casualty
        #Collmap[p2.sf-7][p1.sf-7] += 1
        return (p2,)
            
def checkcollision(packet, packetsAtBS, maxBSReceives,env):
    col = 0 # flag needed since there might be several collisions for packet
    processing = 0
    #print ("MAX RECEIVE IS: ", maxBSReceives)
    for i in range(0,len(packetsAtBS)):
        if packetsAtBS[i].header.processed == 1 or packetsAtBS[i].intraPacket.processed == 1:
            processing = processing + 1
    if (processing > maxBSReceives):
        packet.processed = 0
    else:
        packet.processed = 1
    if packetsAtBS:
        #print ("{:3.5f} || >> FOUND overlap... node {} (sf:{} bw:{} freq:{}) others: {}".format(env.now,packet.nodeid, packet.sf, packet.bw,packet.freq,len(packetsAtBS)))
        for other in packetsAtBS:
            if other.nodeid != packet.nodeid:
                #print ("{:3.5f} || >> node {} overlapped with node {} (sf:{} bw:{} freq:{}). Let's check Freq...".format(env.now,packet.nodeid, other.nodeid, other.packet.sf, other.packet.bw,other.packet.freq))
                # simple collision
                #if frequencyCollision(packet, other.packet) and sfCollision(packet, other.packet):
                if frequencyCollision(packet, other.header):# and timingCollision(packet, other.packet):
                    c = powerCollision_2(packet, other.header,env)
                    for p in c:
                        p.col = 1
                        if p == packet:
                            col = 1
                if frequencyCollision(packet, other.intraPacket):# and timingCollision(packet, other.packet):
                    c = powerCollision_2(packet, other.intraPacket,env)
                    for p in c:
                        p.col = 1
                        if p == packet:
                            col = 1
        return col
    return 0

    
def frequencyCollision(p1,p2):
    if (p1.ch == p2.ch):
        #print ("{:3.5f} || >> same channel for header on node {} and node {}.. Let's check sub-channels...".format(env.now,p1.nodeid,p2.nodeid))
        #if (p1.freqHopHeader[replica] == p2.freqHopHeader[replica]):
        if (p1.subCh == p2.subCh):
            #print ("{:3.5f} || >> same sub-channel for header on node {} and node {}".format(env.now,p1.nodeid,p2.nodeid))
            #print ("{:3.5f} || >> Header {} from node {} collided!!!".format(env.now,replica,p1.nodeid))
            return True
        else:
            #print ("{:3.5f} || >> No sub-channel collision".format(env.now))
            return False
    else:
        #print ("{:3.5f} || >> No header channel collision..".format(env.now))
        return False




def airtime(sf,cr,pl,bw):
    H = 0        # implicit header disabled (H=0) or not (H=1)
    DE = 0       # low data rate optimization enabled (=1) or not (=0)
    Npream = 8   # number of preamble symbol (12.25  from Utz paper)

    if bw == 125 and sf in [11, 12]:
        # low data rate optimization mandated for BW125 with SF11 and SF12
        DE = 1
    if sf == 6:
        # can only have implicit header with SF6
        H = 1

    Tsym = (2.0**sf)/bw
    Tpream = (Npream + 4.25)*Tsym
    #print ("PARAMS FOR TRANSMISION: sf", sf, " cr", cr, "pl", pl, "bw", bw)
    payloadSymbNB = 8 + max(math.ceil((8.0*pl-4.0*sf+28+16-20*H)/(4.0*(sf-2*DE)))*(cr+4),0)
    Tpayload = payloadSymbNB * Tsym
    return ((Tpream + Tpayload)/1000) ##IN SECS
