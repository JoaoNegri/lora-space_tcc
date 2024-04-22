import simpy
import random
import numpy as np
import math
import random
import os
import sys
from aux import checkcollision
from Node import Node


mode_debbug = 0

beacon_rec = 0
max_rec = 15

# if not mode_debbug:
#     null = open(os.devnull, 'w')
#     old_stdout = sys.stdout
#     sys.stdout = null
###WE START BY USING SF=12 ADN BW=125 AND CR=1, FOR ALL NODES AND ALL TRANSMISIONS######

if mode_debbug:
    RANDOM_SEED = 5
    chan = 1
    packetlen = 20
    total_data = 60
    beacon_time = 120
    maxBSReceives = 500
    multi_nodes = [1500]
else:
    RANDOM_SEED = int(sys.argv[1])
    chan = int(sys.argv[2])
    packetlen = int(sys.argv[3])   ##NODES SEND PACKETS OF JUST 20 Bytes
    total_data = int(sys.argv[4]) ##TOTAL DATA ON BUFFER, FOR EACH NODE (IT'S THE BUFFER O DATA BEFORE START SENDING)
    beacon_time = int(sys.argv[5]) ###SAT SENDS BEACON EVERY CERTAIN TIME
    maxBSReceives = int(sys.argv[6]) ##MAX NUMBER OF PACKETS THAT BS (ie SATELLITE) CAN RECEIVE AT SAME TIME
    
    #multi_nodes = [int(sys.argv[7]), int(sys.argv[8]) ,int(sys.argv[9])]
    multi_nodes = [int(sys.argv[7]), int(sys.argv[8]) ,int(sys.argv[9]), int(sys.argv[10]),int(sys.argv[11]),int(sys.argv[12]),int(sys.argv[13]),int(sys.argv[14]),int(sys.argv[15]),int(sys.argv[16]),int(sys.argv[17]),int(sys.argv[18]),int(sys.argv[19]),int(sys.argv[20])]
    p_skip_param = int(sys.argv[21])

    sim_type = sys.argv[22]
nodesToSend = []
packetsToSend = math.ceil(total_data/packetlen)
###GLOBAL PARAMS ####
bsId = 1 ##ID OF BASE STATION (NOT USED)

avgSendTime = 3  ## NOT USED! --> A NODE SENDS A PACKET EVERY X SECS

back_off = beacon_time * 0.95 ###BACK OFF TIME FOR SEND A PACKET
packetsAtBS = [] ##USED FOR CHEK IF THERE ARE ALREADY PACKETS ON THE SATELLITE
c = 299792.458 ###SPEED LIGHT [km/s]
Ptx = 14
G_device = 0; ##ANTENNA GAIN FOR AN END-DEVICE
G_sat = 12;   ##ANTENNA GAIN FOR SATELLITE
nodes = [] ###EACH NODE WILL BE APPENDED TO THIS VARIABLE
freq =868e6 ##USED FOR PATH LOSS CALCULATION
frequency = [868100000, 868300000, 868500000] ##FROM LORAWAN REGIONAL PARAMETERS EU863-870 / EU868


nrLost = 0 ### TOTAL OF LOST PACKETS DUE Lpl
nrCollisions = 0 ##TOTAL OF COLLIDED PACKETS
nrProcessed = 0 ##TOTAL OF PROCESSED PACKETS
nrReceived = 0 ###TOTAL OF RECEIVED PACKETS
nrNoProcessed = 0 ##TOTAL OF INTRA-PACKETS NO PROCESSED
nrIntraTot = 0
nrLostMaxRec = 0
nrCollFullPacket = 0
nrSentIntra = 0 ##TOTAL OF SENT INTRA-PACKTES
nrReceivedIntra = 0 ##TOTAL OF RECEIVED INTRA-PACKETS


##ARRAY WITH MEASURED VALUES FOR SENSIBILITY, NEW VALUES
##THE FOLLOWING VALUES CORRESPOND TO:
#   - FIRST ELEMENT: IT'S THE SF (NOT USABLE)
#   - SECOND ELEMENT: SENSIBILITY FOR 125KHZ BW
#   - THIRD ELEMENT: SENSIBILITY FOR 250KHZ BW
#   - FOURTH ELEMENT: SENSIBILITY FOR 500KHZ BW
# NOTICE THAT SENSIBILITY DECREASE ALONG BW INCREASES, ALSO WITH LOWER SF
# THIS VALUES RESPONDS TO:
# wf = -174 + 10 log(BW) +NF +SNRf
sf7 = np.array([7,-123,-120,-117.0])
sf8 = np.array([8,-126,-123,-120.0])
sf9 = np.array([9,-129,-126,-123.0])
sf10 = np.array([10,-132,-129,-126.0])
sf11 = np.array([11,-134.53,-131.52,-128.51])
sf12 = np.array([12,-137,-134,-131.0])

sensi = np.array([sf7,sf8,sf9,sf10,sf11,sf12])

#DR = ["dr8","dr9","dr10","dr11"]
DR = [-137,-134.5,-134,-131.5]

## READ PARAMS FROM DIRECTORY ##
path = "../params/wider_scenario_2/"

### -137dB IS THE MINIMUN TOLERABLE SENSIBILITY, FOR SF=12 AND BW=125KHz ###

leo_pos=[np.loadtxt( path + "LEO-XYZ-Pos_sat1.csv",skiprows=1,delimiter=',',usecols=(1,2,3)), 
         np.loadtxt( path + "LEO-XYZ-Pos_sat2.csv",skiprows=1,delimiter=',',usecols=(1,2,3))]
## WHERE:
    ## leo_pos[i,j]:
        ## i --> the step time in sat pass
        ## j --> 0 for x-position, 1 for y-position, 2 for z-position
num_sat = len(leo_pos)

sites_pos = np.loadtxt( path + "SITES-XYZ-Pos.csv",skiprows=1,delimiter=',',usecols=(1,2,3))
## WHERE:
    ## sites_pos[i,j]:
        ## i --> the node i
        ## j --> 0 for x-position, 1 for y-position, 2 for z-position

dist_sat = np.zeros((sites_pos.shape[0],len(leo_pos),3,leo_pos[0].shape[0]))
t = 0
for i in range(leo_pos[0].shape[0]):
    t+=1
    for j in range(len(leo_pos)):
        dist_sat [:,j,:,i] = leo_pos[j][i,:] - sites_pos
## WHERE:
    ## dist_sat[i,j,k,l]:
        ## i --> the node i
        ## j --> the sat j
        ## k --> 0 for x-position, 1 for y-position, 2 for z-position
        ## l --> the step time in sat pass
print(dist_sat.shape)

#### FOR COMPUTE DISTANCE MAGNITUDE (ABS) FROM END-DEVICE TO SAT PASSING BY ####
distance = np.zeros((sites_pos.shape[0], len(leo_pos), leo_pos[0].shape[0]))
for j in range(len(leo_pos)):
    distance[:,j,:] = (dist_sat[:,j,0,:]**2 + dist_sat[:,j,1,:]**2 + dist_sat[:,j,2,:]**2)**(1/2)
#TODO ALTERAR O VALOR NO SAT1 e SAT2 para quando estiver fora de alcance não ser 0,0,0 e sim algo bemmmm mais distante
## WHERE:
    ## distance[i,j,k]:
        ## i --> the node i
        ## j --> the sat j
        ## k --> the step time in sat pass


##MATRIX FOR LINK BUDGET, USING Prx ###
Prx = np.zeros((sites_pos.shape[0],len(leo_pos),leo_pos[0].shape[0])) 
Prx = Ptx + G_sat + G_device -20*np.log10(distance*1000) - 20*np.log10(freq) + 147.55 #DISTANCE IS CONVERTED TO METERS
## WHERE:
    ## Prx[i,j,k]:
        ## i --> the node i
        ## j --> the sat j 
        ## k --> the step time in sat pass 

#tinha


# Lpl = np.concatenate((Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,\
#                       Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl,Lpl))

# Prx = np.concatenate((Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,\
#                       Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx,Prx))

elev = np.degrees(np.arcsin(599/distance))

# =============================================================================
# IS7 = np.array([1,-8,-9,-9,-9,-9])
# IS8 = np.array([-11,1,-11,-12,-13,-13])
# IS9 = np.array([-15,-13,1,-13,-14,-15])
# IS10 = np.array([-19,-18,-17,1,-17,-18])
# IS11 = np.array([-22,-22,-21,-20,1,-20])
# IS12 = np.array([-25,-25,-25,-24,-23,1])
# IsoThresholds = np.array([IS7,IS8,IS9,IS10,IS11,IS12])
# 
# =============================================================================


#THIS IS THE MATRIX OF CROSS INTERFERENCE BETWEEN SF


def simulate_scenario (nrNodes, sim_type):
    random.seed(RANDOM_SEED) #RANDOM SEED IS FOR GENERATE ALWAYS THE SAME RANDOM NUMBERS (ie SAME RESULTS OF SIMULATION)
    nodes = [] ###EACH NODE WILL BE APPENDED TO THIS VARIABLE
    logs = []
    for sat in range(num_sat):
        logs.append([])

    for i in range(nrNodes):
        node = Node(i,bsId, avgSendTime, packetlen, total_data, distance, elev, channel, Ptx, Prx, frequency, num_sat)
        nodes.append(node)

    def transmit_eb(env: simpy.Environment,node:Node, sat:int,seed: int):
        random.seed(seed)
        #while nodes[node.nodeid].buffer > 0.0:
        global wait_min
        global wait_max
        global back_off
        global beacon_time
        global nodesToSend
        global DR
        while node.buffer[sat] > 0.0:
            #######STARTS TRANSMISSION AS DR84
            node.dr = 8
            node.sensi = -137
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            #######
            yield env.timeout(node.packet.rectime + float(node.packet.proptime[sat,math.ceil(env.now)])) ##GIVE TIME TO RECEIVE BEACON
            #TODO Verificar se está com o comportamento esperado!!
            if node in packetsAtBS:
                print ("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[12 - 7, [125,250,500].index(node.packet.bw) + 1]
                if Prx[node.nodeid%len(distance)][sat, math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.header.lost = False
                    node.intraPacket.lost = False
                    trySend = False
                    nIntraPackets = 0
                else:
                    nodesToSend.append(node.nodeid)
                    #TODO VERIFICAR NODESTOSEND
                    wait = random.uniform(1,back_off - node.packet.rectime - float(node.packet.proptime[sat, math.ceil(env.now)])) ##TRIGGER BACK-OFF TIME
                    #TODO verificar [0] !!!!!! aqui tem q pensar bem
                    yield env.timeout(wait)
                    #print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    trySend = True
                    node.sent[sat] = node.sent[sat] + 1
                    node.buffer[sat] = node.buffer[sat] - node.packetlen
                    if node in packetsAtBS:
                        print ("{} || ERROR: packet is already in...".format(env.now))
                    else:
                        #sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        sensibility = node.sensi
                        #print ("------Sensi is: ",sensibility)
                        if Prx[node.nodeid%len(distance)][sat, math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                        #TODO verificar [0] !!!!!! aqui tem q pensar bem
                        
                            print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                            node.header.lost = True ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = True ## LOST ONLY CONSIDERING Lpl
                            #nIntraPackets = 0
                            print ("###############lost !!!!!!!!")
                        else:
                            node.header.lost = False ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = False ## LOST ONLY CONSIDERING Lpl
                            #print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                            #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                        
                        for i in range(len(node.header.freqHopHeader)):
                            ###print ("{:3.5f} || Sending Header replica {} node {}...".format(env.now,i,node.nodeid))
                            ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                            node.header.subCh = node.header.freqHopHeader[i]
                            #print ("SUBCHANELLLL: ",node.header.subCh)
                            node.header.sentIntra +=1
                            isLost =0
                            if Prx[node.nodeid%len(Prx)][sat,math.ceil(env.now)] < sensibility:
                                #TODO verificar [0] !!!!!! aqui tem q pensar bem
                                node.header.Nlost +=1
                                isLost =1
                            if (checkcollision(node.header, packetsAtBS, maxBSReceives ,Prx, sat,env)==1):
                                #pass
                                if node.header.col == 1:
                                    if isLost == 0:
                                        node.header.collided +=1
                                #node.packet.collided = 1
                                #print ("---{:3.5f} || Collision for Header replica {} node {} !!!".format(env.now,i,node.nodeid))
                                #node.packet.collided = 1
                                #node.header.collided +=1 #ALREADY COUNTED IN FUNCTION                                
                            else:
                                ###print ("{:3.5f} || ...No Collision for Header replica {} node {}!".format(env.now,i,node.nodeid))
                                #node.packet.collided = 0
                                node.header.noCollided = 1 ##ALMOST ONE HEADER IS OK, THEN HEADER IS OK
                            packetsAtBS.append(node)
                            node.packet.addTime = env.now
                            isLost =0
                        
                            yield env.timeout(node.header.rectime)
                            if (node in packetsAtBS):
                                packetsAtBS.remove(node)
                        
                        ##CALCULATE N OF INTRAPACKETS BASED ON PACKETLEN
                        #payloadTime = airtime(12,1,node.packetlen,125)
                        if node.dr == 8 or node.dr == 10:
                            payloadTime = 1.85 - 0.233*3 
                        elif node.dr == 9 or node.dr ==11:
                            payloadTime = 1.07 - 0.233*2
                        
                        nIntraPackets = math.ceil(payloadTime / 50e-3)
                        #print ("NUMBER OF INTRA PACKETSSSS",nIntraPackets)
                        
                        for j in range (nIntraPackets):
                            ###print ("{:3.5f} || Sending intra-packet {} of {} for node {}...".format(env.now,j,nIntraPackets-1,node.nodeid))
                            ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                            node.intraPacket.subCh = node.intraPacket.freqHopIntraPacket[j]
                            node.intraPacket.sentIntra +=1
                            isLost =0
                            if Prx[node.nodeid%len(distance)][sat, math.ceil(env.now)] < sensibility:
                                #TODO verificar [0] !!!!!! aqui tem q pensar bem

                                node.intraPacket.Nlost +=1
                                isLost =1
                            #print ("INTRA-PACKT SUB CHANNELLLL", node.intraPacket.subCh)
                            if (checkcollision(node.intraPacket, packetsAtBS, maxBSReceives,Prx, sat,env)==1):
                                #pass
                                if node.intraPacket.col == 1:
                                    if isLost ==0:
                                        node.intraPacket.collided+=1
                                #print ("---{:3.5f} || Collision for intra-packet {} for node {} !!!".format(env.now,j,node.nodeid))
                                #node.intraPacket.collided+=1 #ALREADY COUNTED ON FUNCTION
                            else:
                                ###print ("{:3.5f} || ...No Collision for intra-packet {} for node {}!".format(env.now,j,node.nodeid))
                                node.intraPacket.noCollided +=1
                                pass
                            packetsAtBS.append(node)
                            node.packet.addTime = env.now
                            isLost =0
                            yield env.timeout(node.intraPacket.rectime)
                            if (node in packetsAtBS):
                                packetsAtBS.remove(node)
                            #print ("INTRA-PACKET NO-PROCESEDDD",node.intraPacket.noProcessed)
            
            node.header.noCollided = len(node.header.freqHopHeader)-node.header.Nlost-node.header.collided
            node.intraPacket.noCollided = nIntraPackets-node.intraPacket.Nlost-node.intraPacket.collided
            if node.header.noCollided <0:
                node.header.noCollided = 0
            if node.intraPacket.noCollided <0:
                node.intraPacket.noCollided = 0
                
            if trySend == 1 and sat==0:
                #print ("----count intra-packet collided", node.intraPacket.collided)
                if node.header.lost or node.intraPacket.lost:
                    logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                else:
                    if node.dr ==8 or node.dr==10:
                        if node.header.collided == 3:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (1/3)*nIntraPackets:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 3:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (1/3)*nIntraPackets:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                                   
                    elif node.dr==9 or node.dr==11:
                        if node.header.collided == 2:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (2/3)*nIntraPackets:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 2:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (2/3)*nIntraPackets:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[sat, math.ceil(env.now)],0,node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
            
            ##RESET
            node.header.collided = 0
            node.header.processed = 0
            node.header.noProcessed = 0
            node.header.lost = False
            node.header.noCollided =0
            node.intraPacket.nrColl = 0
            node.intraPacket.collided = 0
            node.intraPacket.processed = 0
            node.intraPacket.noProcessed = 0
            node.intraPacket.lost = False
            node.intraPacket.noCollided = 0
            node.header.sentIntra = 0
            node.intraPacket.sentIntra = 0
            node.header.Nlost =0
            node.intraPacket.Nlost = 0
            
            if trySend:
                #print ("BEACON TIMEEE",beacon_time)
                #print ("WAITTT",wait)
                #print ("NODE HEADER TIME",node.header.rectime)
                #print ("ONE INTRA-PACKET TIMEE",node.intraPacket.rectime)
                #yield env.timeout(beacon_time-wait)
                yield env.timeout(beacon_time-wait-2*3*node.header.rectime-2*nIntraPackets*node.intraPacket.rectime)
            else:
                nIntraPackets = 0
                yield env.timeout(beacon_time-wait-3*node.header.rectime-nIntraPackets*node.intraPacket.rectime)

    def transmit_etr(env,node):
        #while nodes[node.nodeid].buffer > 0.0:
        global wait_min
        global wait_max
        global back_off
        global beacon_time
        global nodesToSend
        global DR
        while node.buffer > 0.0:
            #######STARTS TRANSMISSION AS DR8
            node.dr = 8
            node.sensi = -137
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            #######
            yield env.timeout(node.packet.rectime + float(node.packet.proptime[math.ceil(env.now)])) ##GIVE TIME TO RECEIVE BEACON
                          
            if node in packetsAtBS:
                print ("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[12 - 7, [125,250,500].index(node.packet.bw) + 1]
                if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.header.lost = False
                    node.intraPacket.lost = False
                    trySend = False
                    nIntraPackets = 0
                else:
                    nodesToSend.append(node.nodeid)
                    wait = random.uniform(1,back_off - node.packet.rectime - float(node.packet.proptime[math.ceil(env.now)])) ##TRIGGER BACK-OFF TIME
                    yield env.timeout(wait)
                    #print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    #trySend = True
                    trySend = selectDR_etr(env,node)
                    if node in packetsAtBS:
                        print ("{} || ERROR: packet is already in...".format(env.now))
                    elif trySend == 1:
                        #sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        sensibility = node.sensi
                        node.sent = node.sent + 1
                        node.buffer = node.buffer - node.packetlen
                        #print ("------Sensi is: ",sensibility)
                        if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                            print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                            node.header.lost = True ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = True ## LOST ONLY CONSIDERING Lpl
                            nIntraPackets = 0
                            print ("###############lost !!!!!!!!")
                        else:
                            node.header.lost = False ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = False ## LOST ONLY CONSIDERING Lpl
                            
                            #print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                            #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                           
                            for i in range(len(node.header.freqHopHeader)):
                                ###print ("{:3.5f} || Sending Header replica {} node {}...".format(env.now,i,node.nodeid))
                                ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                node.header.subCh = node.header.freqHopHeader[i]
                                #print ("SUBCHANELLLL: ",node.header.subCh)
                                node.header.sentIntra +=1;
                                isLost =0
                                if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                    node.header.Nlost +=1
                                    isLost =1
                                if (checkcollision(node.header, packetsAtBS, maxBSReceives,env)==1):
                                    #pass
                                    if node.header.col ==1:
                                        if isLost == 0:
                                            node.header.collided +=1
                                    #node.packet.collided = 1
                                    #print ("---{:3.5f} || Collision for Header replica {} node {} !!!".format(env.now,i,node.nodeid))
                                    #node.packet.collided = 1
                                    #node.header.collided +=1 #ALREADY COUNTED IN FUNCTION                                
                                else:
                                    ###print ("{:3.5f} || ...No Collision for Header replica {} node {}!".format(env.now,i,node.nodeid))
                                    #node.packet.collided = 0
                                    node.header.noCollided = 1 ##ALMOST ONE HEADER IS OK, THEN HEADER IS OK
                                packetsAtBS.append(node)
                                node.packet.addTime = env.now
                                isLost =0
                            
                                yield env.timeout(node.header.rectime)
                                if (node in packetsAtBS):
                                    packetsAtBS.remove(node)
                            
                            ##CALCULATE N OF INTRAPACKETS BASED ON PACKETLEN
                            #payloadTime = airtime(12,1,node.packetlen,125)
                            if node.dr == 8 or node.dr == 10:
                                payloadTime = 1.85 - 0.233*3 
                            elif node.dr == 9 or node.dr ==11:
                                payloadTime = 1.07 - 0.233*2
                            
                            nIntraPackets = math.ceil(payloadTime / 50e-3)
                            #print ("NUMBER OF INTRA PACKETSSSS",nIntraPackets)
                            
                            for j in range (nIntraPackets):
                                ###print ("{:3.5f} || Sending intra-packet {} of {} for node {}...".format(env.now,j,nIntraPackets-1,node.nodeid))
                                ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                node.intraPacket.subCh = node.intraPacket.freqHopIntraPacket[j]
                                node.intraPacket.sentIntra +=1
                                isLost =0
                                #print ("INTRA-PACKT SUB CHANNELLLL", node.intraPacket.subCh)
                                if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                    node.intraPacket.Nlost +=1
                                    isLost =1
                                if (checkcollision(node.intraPacket, packetsAtBS, maxBSReceives,env)==1):
                                    #pass
                                    if node.intraPacket.col == 1:
                                        if isLost == 0:
                                            node.intraPacket.collided+=1
                                    #print ("---{:3.5f} || Collision for intra-packet {} for node {} !!!".format(env.now,j,node.nodeid))
                                    #node.intraPacket.collided+=1 #ALREADY COUNTED ON FUNCTION
                                else:
                                    ###print ("{:3.5f} || ...No Collision for intra-packet {} for node {}!".format(env.now,j,node.nodeid))
                                    node.intraPacket.noCollided +=1
                                    pass
                                packetsAtBS.append(node)
                                node.packet.addTime = env.now
                                isLost =0
                                yield env.timeout(node.intraPacket.rectime)
                                if (node in packetsAtBS):
                                    packetsAtBS.remove(node)
                                #print ("INTRA-PACKET NO-PROCESEDDD",node.intraPacket.noProcessed)
            
            node.header.noCollided = len(node.header.freqHopHeader)-node.header.Nlost-node.header.collided
            node.intraPacket.noCollided = nIntraPackets-node.intraPacket.Nlost-node.intraPacket.collided
            if node.header.noCollided <0:
                node.header.noCollided = 0
            if node.intraPacket.noCollided <0:
                node.intraPacket.noCollided = 0
                  
            if trySend == 1:
                #print ("----count intra-packet collided", node.intraPacket.collided)
                if node.header.lost or node.intraPacket.lost:
                    logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                
                else:
                    if node.dr ==8 or node.dr==10:
                        if node.header.collided == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                                   
                    elif node.dr==9 or node.dr==11:
                        if node.header.collided == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
            
            ##RESET
            node.header.collided = 0
            node.header.processed = 0
            node.header.noProcessed = 0
            node.header.lost = False
            node.header.noCollided =0
            node.intraPacket.nrColl = 0
            node.intraPacket.collided = 0
            node.intraPacket.processed = 0
            node.intraPacket.noProcessed = 0
            node.intraPacket.lost = False
            node.intraPacket.noCollided = 0
            node.header.sentIntra = 0
            node.intraPacket.sentIntra = 0
            node.header.Nlost =0
            node.intraPacket.Nlost = 0
            
            if trySend:
                #print ("BEACON TIMEEE",beacon_time)
                #print ("WAITTT",wait)
                #print ("NODE HEADER TIME",node.header.rectime)
                #print ("ONE INTRA-PACKET TIMEE",node.intraPacket.rectime)
                #yield env.timeout(beacon_time-wait)
                yield env.timeout(beacon_time-wait-2*3*node.header.rectime-2*nIntraPackets*node.intraPacket.rectime)
            else:
                nIntraPackets =0
                yield env.timeout(beacon_time-wait-3*node.header.rectime-nIntraPackets*node.intraPacket.rectime)

    def selectDR_etr (env,node):
        global DR
        dr = [8,9,10,11]
        rssi = node.packet.rssi[math.ceil(env.now)]
        if rssi > DR[3]:
            #print ("----Select DR11")
            node.dr = random.choice([11,10,9])
            node.header.dr = node.dr
            node.intraPacket.dr = node.dr   
        elif rssi > DR[2]:
            #print ("----Select DR10")
            node.dr = random.choice([10,9,8])
            node.header.dr = node.dr
            node.intraPacket.dr = node.dr
        elif rssi > DR[1]:
            #print ("----Select DR9")
            node.dr = random.choice([9,8])
            node.header.dr = node.dr
            node.intraPacket.dr = node.dr
        elif rssi > DR[0]:
            #print ("----Select DR8")
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
        else:
            #print ("----Select DR8")
            node.dr = 0
            node.header.dr = 8
            node.intraPacket.dr = 8
            
        if node.dr == 11:
            node.sensi = DR[3]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif node.dr == 10:
            node.sensi = DR[2]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        elif node.dr == 9:
            node.sensi = DR[1]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif node.dr == 8:
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        else:
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            print ("-----NO SEND!!")
            return (0)

    def transmit_etbr(env,node):
        #while nodes[node.nodeid].buffer > 0.0:
        global wait_min
        global wait_max
        global back_off
        global beacon_time
        global nodesToSend
        global DR
        global beacon_rec
        global p_skip_param
        while node.buffer > 0.0:
            #######STARTS TRANSMISSION AS DR8
            node.dr = 8
            node.sensi = -137
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            #######
            yield env.timeout(node.packet.rectime + float(node.packet.proptime[math.ceil(env.now)])) ##GIVE TIME TO RECEIVE BEACON
                          
            if node in packetsAtBS:
                print ("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[12 - 7, [125,250,500].index(node.packet.bw) + 1]
                if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.header.lost = False
                    node.intraPacket.lost = False
                    trySend = False
                    nIntraPackets = 0
                else:
                    nodesToSend.append(node.nodeid)
                    beacon_rec += 1
                    wait = random.uniform(1,back_off - node.packet.rectime - float(node.packet.proptime[math.ceil(env.now)])) ##TRIGGER BACK-OFF TIME
                    yield env.timeout(wait)
                    #print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    #trySend = True
                    trySend = selectDR_etbr(env,node)
                    if node in packetsAtBS:
                        print ("{} || ERROR: packet is already in...".format(env.now))
                    elif trySend == 1:
                        #sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        sensibility = node.sensi
                        #print ("------Sensi is: ",sensibility)
                        p_skip = 2/(1+math.exp(-beacon_rec/p_skip_param))-1
                        this_p = random.uniform(0,1)
                        if this_p < p_skip:
                            trySend =0
                            nIntraPackets = 0
                        else:
                            node.sent = node.sent + 1
                            node.buffer = node.buffer - node.packetlen
                            if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                                print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                                node.header.lost = True ## LOST ONLY CONSIDERING Lpl
                                node.intraPacket.lost = True ## LOST ONLY CONSIDERING Lpl
                                nIntraPackets = 0
                                print ("###############lost !!!!!!!!")
                            else:
                                node.header.lost = False ## LOST ONLY CONSIDERING Lpl
                                node.intraPacket.lost = False ## LOST ONLY CONSIDERING Lpl
                                #print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                                #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                               
                                for i in range(len(node.header.freqHopHeader)):
                                    ###print ("{:3.5f} || Sending Header replica {} node {}...".format(env.now,i,node.nodeid))
                                    ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                    node.header.subCh = node.header.freqHopHeader[i]
                                    #print ("SUBCHANELLLL: ",node.header.subCh)
                                    node.header.sentIntra +=1;
                                    isLost =0
                                    if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                        node.header.Nlost +=1
                                        isLost =1
                                    if (checkcollision(node.header, packetsAtBS, maxBSReceives,env)==1):
                                        #pass
                                        if node.header.col ==1:
                                            if isLost == 0:
                                                node.header.collided +=1
                                        #node.packet.collided = 1
                                        #print ("---{:3.5f} || Collision for Header replica {} node {} !!!".format(env.now,i,node.nodeid))
                                        #node.packet.collided = 1
                                        #node.header.collided +=1 #ALREADY COUNTED IN FUNCTION                                
                                    else:
                                        ###print ("{:3.5f} || ...No Collision for Header replica {} node {}!".format(env.now,i,node.nodeid))
                                        #node.packet.collided = 0
                                        node.header.noCollided = 1 ##ALMOST ONE HEADER IS OK, THEN HEADER IS OK
                                    packetsAtBS.append(node)
                                    node.packet.addTime = env.now
                                    isLost =0
                                
                                    yield env.timeout(node.header.rectime)
                                    if (node in packetsAtBS):
                                        packetsAtBS.remove(node)
                                
                                ##CALCULATE N OF INTRAPACKETS BASED ON PACKETLEN
                                #payloadTime = airtime(12,1,node.packetlen,125)
                                if node.dr == 8 or node.dr == 10:
                                    payloadTime = 1.85 - 0.233*3 
                                elif node.dr == 9 or node.dr ==11:
                                    payloadTime = 1.07 - 0.233*2
                                
                                nIntraPackets = math.ceil(payloadTime / 50e-3)
                                #print ("NUMBER OF INTRA PACKETSSSS",nIntraPackets)
                                
                                for j in range (nIntraPackets):
                                    ###print ("{:3.5f} || Sending intra-packet {} of {} for node {}...".format(env.now,j,nIntraPackets-1,node.nodeid))
                                    ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                    node.intraPacket.subCh = node.intraPacket.freqHopIntraPacket[j]
                                    node.intraPacket.sentIntra +=1
                                    #print ("INTRA-PACKT SUB CHANNELLLL", node.intraPacket.subCh)
                                    isLost =0
                                    if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                        node.intraPacket.Nlost +=1
                                        isLost =1
                                    if (checkcollision(node.intraPacket, packetsAtBS, maxBSReceives,env)==1):
                                        #pass
                                        if node.intraPacket.col ==1:
                                            if isLost == 0:
                                                node.intraPacket.collided+=1
                                        #print ("---{:3.5f} || Collision for intra-packet {} for node {} !!!".format(env.now,j,node.nodeid))
                                        #node.intraPacket.collided+=1 #ALREADY COUNTED ON FUNCTION
                                    else:
                                        ###print ("{:3.5f} || ...No Collision for intra-packet {} for node {}!".format(env.now,j,node.nodeid))
                                        node.intraPacket.noCollided +=1
                                        pass
                                    packetsAtBS.append(node)
                                    node.packet.addTime = env.now
                                    isLost =0
                                    yield env.timeout(node.intraPacket.rectime)
                                    if (node in packetsAtBS):
                                        packetsAtBS.remove(node)
                                    #print ("INTRA-PACKET NO-PROCESEDDD",node.intraPacket.noProcessed)
            
            node.header.noCollided = len(node.header.freqHopHeader)-node.header.Nlost-node.header.collided
            node.intraPacket.noCollided = nIntraPackets-node.intraPacket.Nlost-node.intraPacket.collided
            if node.header.noCollided <0:
                node.header.noCollided = 0
            if node.intraPacket.noCollided <0:
                node.intraPacket.noCollided = 0
                
            if trySend == 1:
                #print ("----count intra-packet collided", node.intraPacket.collided)
                if node.header.lost or node.intraPacket.lost:
                    logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                
                else:
                    if node.dr ==8 or node.dr==10:
                        if node.header.collided == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                                   
                    elif node.dr==9 or node.dr==11:
                        if node.header.collided == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
            
            ##RESET
            node.header.collided = 0
            node.header.processed = 0
            node.header.noProcessed = 0
            node.header.lost = False
            node.header.noCollided =0
            node.intraPacket.nrColl = 0
            node.intraPacket.collided = 0
            node.intraPacket.processed = 0
            node.intraPacket.noProcessed = 0
            node.intraPacket.lost = False
            node.intraPacket.noCollided = 0
            node.header.sentIntra = 0
            node.intraPacket.sentIntra = 0
            node.header.Nlost =0
            node.intraPacket.Nlost = 0
            
            if trySend:
                #print ("BEACON TIMEEE",beacon_time)
                #print ("WAITTT",wait)
                #print ("NODE HEADER TIME",node.header.rectime)
                #print ("ONE INTRA-PACKET TIMEE",node.intraPacket.rectime)
                #yield env.timeout(beacon_time-wait)
                yield env.timeout(beacon_time-wait-2*3*node.header.rectime-2*nIntraPackets*node.intraPacket.rectime)
            else:
                nIntraPackets = 0
                yield env.timeout(beacon_time-wait-3*node.header.rectime-nIntraPackets*node.intraPacket.rectime)

    def selectDR_etbr (env,node):
        global DR
        dr = [8,9,10,11]
        rssi = node.packet.rssi[math.ceil(env.now)]
        if rssi > DR[3]:
            #print ("----Select DR11")
            node.dr = random.choice([11,10,9])
            node.header.dr = node.dr
            node.intraPacket.dr = node.dr   
        elif rssi > DR[2]:
            #print ("----Select DR10")
            node.dr = random.choice([10,9,8])
            node.header.dr = node.dr
            node.intraPacket.dr = node.dr
        elif rssi > DR[1]:
            #print ("----Select DR9")
            node.dr = random.choice([9,8])
            node.header.dr = node.dr
            node.intraPacket.dr = node.dr
        elif rssi > DR[0]:
            #print ("----Select DR8")
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
        else:
            #print ("----Select DR8")
            node.dr = 0
            node.header.dr = 8
            node.intraPacket.dr = 8
            
        if node.dr == 11:
            node.sensi = DR[3]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif node.dr == 10:
            node.sensi = DR[2]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        elif node.dr == 9:
            node.sensi = DR[1]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif node.dr == 8:
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        else:
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            print ("-----NO SEND!!")
            return (0)

    def transmit_et(env,node):
        #while nodes[node.nodeid].buffer > 0.0:
        global wait_min
        global wait_max
        global back_off
        global beacon_time
        
        global nodesToSend
        global DR
        while node.buffer > 0.0:
            #######STARTS TRANSMISSION AS DR8
            node.dr = 8
            node.sensi = -137
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            #######
            yield env.timeout(node.packet.rectime + float(node.packet.proptime[math.ceil(env.now)])) ##GIVE TIME TO RECEIVE BEACON
                          
            if node in packetsAtBS:
                print ("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[12 - 7, [125,250,500].index(node.packet.bw) + 1]
                if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.header.lost = False
                    node.intraPacket.lost = False
                    trySend = False
                    nIntraPackets = 0
                else:
                    nodesToSend.append(node.nodeid)
                    wait = random.uniform(1,back_off - node.packet.rectime - float(node.packet.proptime[math.ceil(env.now)])) ##TRIGGER BACK-OFF TIME
                    yield env.timeout(wait)
                    #print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    #trySend = True
                    trySend = selectDR_et(env,node)
                    if node in packetsAtBS:
                        print ("{} || ERROR: packet is already in...".format(env.now))
                    elif trySend == 1:
                        #sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        sensibility = node.sensi
                        #print ("------Sensi is: ",sensibility)
                        node.sent = node.sent + 1
                        node.buffer = node.buffer - node.packetlen
                        if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                            print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                            node.header.lost = True ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = True ## LOST ONLY CONSIDERING Lpl
                            nIntraPackets = 0
                            print ("###############lost !!!!!!!!")
                        else:
                            node.header.lost = False ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = False ## LOST ONLY CONSIDERING Lpl
                            
                            #print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                            #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                           
                            for i in range(len(node.header.freqHopHeader)):
                                ###print ("{:3.5f} || Sending Header replica {} node {}...".format(env.now,i,node.nodeid))
                                ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                node.header.subCh = node.header.freqHopHeader[i]
                                #print ("SUBCHANELLLL: ",node.header.subCh)
                                node.header.sentIntra +=1;
                                isLost =0
                                if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                    node.header.Nlost +=1
                                    isLost =1
                                if (checkcollision(node.header, packetsAtBS, maxBSReceives,env)==1):
                                    #pass
                                    if node.header.col == 1:
                                        if isLost == 0:
                                            node.header.collided +=1
                                    #node.packet.collided = 1
                                    #print ("---{:3.5f} || Collision for Header replica {} node {} !!!".format(env.now,i,node.nodeid))
                                    #node.packet.collided = 1
                                    #node.header.collided +=1 #ALREADY COUNTED IN FUNCTION                                
                                else:
                                    ###print ("{:3.5f} || ...No Collision for Header replica {} node {}!".format(env.now,i,node.nodeid))
                                    #node.packet.collided = 0
                                    node.header.noCollided = 1 ##ALMOST ONE HEADER IS OK, THEN HEADER IS OK
                                packetsAtBS.append(node)
                                node.packet.addTime = env.now
                                isLost =0
                            
                                yield env.timeout(node.header.rectime)
                                if (node in packetsAtBS):
                                    packetsAtBS.remove(node)
                            
                            ##CALCULATE N OF INTRAPACKETS BASED ON PACKETLEN
                            #payloadTime = airtime(12,1,node.packetlen,125)
                            if node.dr == 8 or node.dr == 10:
                                payloadTime = 1.85 - 0.233*3 
                            elif node.dr == 9 or node.dr ==11:
                                payloadTime = 1.07 - 0.233*2
                            
                            nIntraPackets = math.ceil(payloadTime / 50e-3)
                            #print ("NUMBER OF INTRA PACKETSSSS",nIntraPackets)
                            
                            for j in range (nIntraPackets):
                                ###print ("{:3.5f} || Sending intra-packet {} of {} for node {}...".format(env.now,j,nIntraPackets-1,node.nodeid))
                                ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                node.intraPacket.subCh = node.intraPacket.freqHopIntraPacket[j]
                                node.intraPacket.sentIntra +=1
                                #print ("INTRA-PACKT SUB CHANNELLLL", node.intraPacket.subCh)
                                isLost =0
                                if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                    node.intraPacket.Nlost +=1
                                    isLost =1
                                if (checkcollision(node.intraPacket, packetsAtBS, maxBSReceives,env)==1):
                                    #pass
                                    if node.intraPacket.col ==1:
                                        if isLost == 0:
                                            node.intraPacket.collided+=1
                                    #print ("---{:3.5f} || Collision for intra-packet {} for node {} !!!".format(env.now,j,node.nodeid))
                                    #node.intraPacket.collided+=1 #ALREADY COUNTED ON FUNCTION
                                else:
                                    ###print ("{:3.5f} || ...No Collision for intra-packet {} for node {}!".format(env.now,j,node.nodeid))
                                    node.intraPacket.noCollided +=1
                                    pass
                                packetsAtBS.append(node)
                                node.packet.addTime = env.now
                                yield env.timeout(node.intraPacket.rectime)
                                if (node in packetsAtBS):
                                    packetsAtBS.remove(node)
                                isLost =0
                                #print ("INTRA-PACKET NO-PROCESEDDD",node.intraPacket.noProcessed)
            
            node.header.noCollided = len(node.header.freqHopHeader)-node.header.Nlost-node.header.collided           
            node.intraPacket.noCollided = nIntraPackets-node.intraPacket.Nlost-node.intraPacket.collided
            #print ("------{} node {}: header col: {} ; intra-packet col: {}".format(env.now,node.nodeid,node.header.collided,node.intraPacket.collided))
            if node.header.noCollided <0:
                node.header.noCollided = 0
            if node.intraPacket.noCollided <0:
                node.intraPacket.noCollided = 0                  
            
            if trySend == 1:
                #print ("----count intra-packet collided", node.intraPacket.collided)
                if node.header.lost or node.intraPacket.lost:
                    logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                
                else:
                    if node.dr ==8 or node.dr==10:
                        if node.header.collided >= 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                                   
                    elif node.dr==9 or node.dr==11:
                        if node.header.collided >= 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
            
            ##RESET
            node.header.collided = 0
            node.header.processed = 0
            node.header.noProcessed = 0
            node.header.lost = False
            node.header.noCollided =0
            node.intraPacket.nrColl = 0
            node.intraPacket.collided = 0
            node.intraPacket.processed = 0
            node.intraPacket.noProcessed = 0
            node.intraPacket.lost = False
            node.intraPacket.noCollided = 0
            node.header.sentIntra = 0
            node.intraPacket.sentIntra = 0
            node.header.Nlost =0
            node.intraPacket.Nlost = 0
            if trySend:
                #print ("BEACON TIMEEE",beacon_time)
                #print ("WAITTT",wait)
                #print ("NODE HEADER TIME",node.header.rectime)
                #print ("ONE INTRA-PACKET TIMEE",node.intraPacket.rectime)
                #yield env.timeout(beacon_time-wait)
                yield env.timeout(beacon_time-wait-2*3*node.header.rectime-2*nIntraPackets*node.intraPacket.rectime)
            else:
                nIntraPackets = 0
                yield env.timeout(beacon_time-wait-3*node.header.rectime-nIntraPackets*node.intraPacket.rectime)

    def selectDR_et (env,node):
        global DR
        rssi = node.packet.rssi[math.ceil(env.now)]
        if rssi > DR[3]:
            #print ("----Select DR11")
            node.dr = 11
            node.header.dr = 11
            node.intraPacket.dr = 11
            node.sensi = DR[3]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif rssi > DR[2]:
            #print ("----Select DR10")
            node.dr = 10
            node.header.dr = 10
            node.intraPacket.dr = 10
            node.sensi = DR[2]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        elif rssi > DR[1]:
            #print ("----Select DR9")
            node.dr = 9
            node.header.dr = 9
            node.intraPacket.dr = 9
            node.sensi = DR[1]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif rssi > DR[0]:
            #print ("----Select DR8")
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        else:
            #print ("----Select DR8")
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (0)
     
    def transmit_etb(env,node):
        #while nodes[node.nodeid].buffer > 0.0:
        global wait_min
        global wait_max
        global back_off
        global beacon_time
        
        global nodesToSend
        global DR
        global beacon_rec
        global p_skip_param
        while node.buffer > 0.0:
            #######STARTS TRANSMISSION AS DR8
            node.dr = 8
            node.sensi = -137
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            #######
            yield env.timeout(node.packet.rectime + float(node.packet.proptime[math.ceil(env.now)])) ##GIVE TIME TO RECEIVE BEACON
                          
            if node in packetsAtBS:
                print ("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[12 - 7, [125,250,500].index(node.packet.bw) + 1]
                if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.header.lost = False
                    node.intraPacket.lost = False
                    trySend = False
                    nIntraPackets = 0
                else:
                    nodesToSend.append(node.nodeid)
                    beacon_rec += 1
                    wait = random.uniform(1,back_off - node.packet.rectime - float(node.packet.proptime[math.ceil(env.now)])) ##TRIGGER BACK-OFF TIME
                    yield env.timeout(wait)
                    #print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    #trySend = True
                    trySend = selectDR_etb(env,node)
                    if node in packetsAtBS:
                        print ("{} || ERROR: packet is already in...".format(env.now))
                    elif trySend == 1:
                        #sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        sensibility = node.sensi
                        #print ("------Sensi is: ",sensibility)
                        p_skip = 2/(1+math.exp(-beacon_rec/p_skip_param))-1
                        this_p = random.uniform(0,1)
                        if this_p < p_skip:
                            trySend =0
                            nIntraPackets = 0
                        else:
                            node.sent = node.sent + 1
                            node.buffer = node.buffer - node.packetlen
                            if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                                print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                                node.header.lost = True ## LOST ONLY CONSIDERING Lpl
                                node.intraPacket.lost = True ## LOST ONLY CONSIDERING Lpl
                                nIntraPackets = 0
                                print ("###############lost !!!!!!!!")
                            else:
                                node.header.lost = False ## LOST ONLY CONSIDERING Lpl
                                node.intraPacket.lost = False ## LOST ONLY CONSIDERING Lpl
                                #print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                                #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                               
                                for i in range(len(node.header.freqHopHeader)):
                                    ###print ("{:3.5f} || Sending Header replica {} node {}...".format(env.now,i,node.nodeid))
                                    ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                    node.header.subCh = node.header.freqHopHeader[i]
                                    #print ("SUBCHANELLLL: ",node.header.subCh)
                                    node.header.sentIntra +=1;
                                    isLost =0
                                    if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                        node.header.Nlost +=1
                                        isLost =1
                                    if (checkcollision(node.header, packetsAtBS, maxBSReceives,env)==1):
                                        #pass
                                        if node.header.col ==1:
                                            if isLost == 0:
                                                node.header.collided +=1
                                        #node.packet.collided = 1
                                        #print ("---{:3.5f} || Collision for Header replica {} node {} !!!".format(env.now,i,node.nodeid))
                                        #node.packet.collided = 1
                                        #node.header.collided +=1 #ALREADY COUNTED IN FUNCTION                                
                                    else:
                                        ###print ("{:3.5f} || ...No Collision for Header replica {} node {}!".format(env.now,i,node.nodeid))
                                        #node.packet.collided = 0
                                        node.header.noCollided = 1 ##ALMOST ONE HEADER IS OK, THEN HEADER IS OK
                                    packetsAtBS.append(node)
                                    node.packet.addTime = env.now
                                    isLost =0
                                
                                    yield env.timeout(node.header.rectime)
                                    if (node in packetsAtBS):
                                        packetsAtBS.remove(node)
                                
                                ##CALCULATE N OF INTRAPACKETS BASED ON PACKETLEN
                                #payloadTime = airtime(12,1,node.packetlen,125)
                                if node.dr == 8 or node.dr == 10:
                                    payloadTime = 1.85 - 0.233*3 
                                elif node.dr == 9 or node.dr ==11:
                                    payloadTime = 1.07 - 0.233*2
                                
                                nIntraPackets = math.ceil(payloadTime / 50e-3)
                                #print ("NUMBER OF INTRA PACKETSSSS",nIntraPackets)
                                
                                for j in range (nIntraPackets):
                                    ###print ("{:3.5f} || Sending intra-packet {} of {} for node {}...".format(env.now,j,nIntraPackets-1,node.nodeid))
                                    ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                                    node.intraPacket.subCh = node.intraPacket.freqHopIntraPacket[j]
                                    node.intraPacket.sentIntra +=1
                                    isLost =0
                                    if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                        node.intraPacket.Nlost +=1
                                        isLost =1
                                    #print ("INTRA-PACKT SUB CHANNELLLL", node.intraPacket.subCh)
                                    if (checkcollision(node.intraPacket, packetsAtBS, maxBSReceives,env)==1):
                                        #pass
                                        if node.intraPacket.col == 1:
                                            if isLost == 0:
                                                node.intraPacket.collided+=1
                                        #print ("---{:3.5f} || Collision for intra-packet {} for node {} !!!".format(env.now,j,node.nodeid))
                                        #node.intraPacket.collided+=1 #ALREADY COUNTED ON FUNCTION
                                    else:
                                        ###print ("{:3.5f} || ...No Collision for intra-packet {} for node {}!".format(env.now,j,node.nodeid))
                                        node.intraPacket.noCollided +=1
                                        pass
                                    packetsAtBS.append(node)
                                    node.packet.addTime = env.now
                                    isLost =0
                                    yield env.timeout(node.intraPacket.rectime)
                                    if (node in packetsAtBS):
                                        packetsAtBS.remove(node)
                                    #print ("INTRA-PACKET NO-PROCESEDDD",node.intraPacket.noProcessed)
            
            node.header.noCollided = len(node.header.freqHopHeader)-node.header.Nlost-node.header.collided
            node.intraPacket.noCollided = nIntraPackets-node.intraPacket.Nlost-node.intraPacket.collided
            if node.header.noCollided <0:
                node.header.noCollided = 0
            if node.intraPacket.noCollided <0:
                node.intraPacket.noCollided = 0
                  
            if trySend == 1:
                #print ("----count intra-packet collided", node.intraPacket.collided)
                if node.header.lost or node.intraPacket.lost:
                    logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                
                else:
                    if node.dr ==8 or node.dr==10:
                        if node.header.collided == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                                   
                    elif node.dr==9 or node.dr==11:
                        if node.header.collided == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
            
            ##RESET
            node.header.collided = 0
            node.header.processed = 0
            node.header.noProcessed = 0
            node.header.lost = False
            node.header.noCollided =0
            node.intraPacket.nrColl = 0
            node.intraPacket.collided = 0
            node.intraPacket.processed = 0
            node.intraPacket.noProcessed = 0
            node.intraPacket.lost = False
            node.intraPacket.noCollided = 0
            node.header.sentIntra = 0
            node.intraPacket.sentIntra = 0
            node.header.Nlost =0
            node.intraPacket.Nlost = 0
            
            if trySend:
                #print ("BEACON TIMEEE",beacon_time)
                #print ("WAITTT",wait)
                #print ("NODE HEADER TIME",node.header.rectime)
                #print ("ONE INTRA-PACKET TIMEE",node.intraPacket.rectime)
                #yield env.timeout(beacon_time-wait)
                yield env.timeout(beacon_time-wait-2*3*node.header.rectime-2*nIntraPackets*node.intraPacket.rectime)
            else:
                nIntraPackets = 0
                yield env.timeout(beacon_time-wait-3*node.header.rectime-nIntraPackets*node.intraPacket.rectime)

    def selectDR_etb (env,node):
        global DR
        rssi = node.packet.rssi[math.ceil(env.now)]
        if rssi > DR[3]:
            #print ("----Select DR11")
            node.dr = 11
            node.header.dr = 11
            node.intraPacket.dr = 11
            node.sensi = DR[3]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif rssi > DR[2]:
            #print ("----Select DR10")
            node.dr = 10
            node.header.dr = 10
            node.intraPacket.dr = 10
            node.sensi = DR[2]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        elif rssi > DR[1]:
            #print ("----Select DR9")
            node.dr = 9
            node.header.dr = 9
            node.intraPacket.dr = 9
            node.sensi = DR[1]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
            return (1)
        elif rssi > DR[0]:
            #print ("----Select DR8")
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (1)
        else:
            #print ("----Select DR8")
            node.dr = 8
            node.header.dr = 8
            node.intraPacket.dr = 8
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            return (0)
        
    def transmit_er(env,node):
        #while nodes[node.nodeid].buffer > 0.0:
        global wait_min
        global wait_max
        global back_off
        global beacon_time
        
        global nodesToSend
        global DR
        while node.buffer > 0.0:
            #######STARTS TRANSMISSION AS DR8
            node.dr = 8
            node.sensi = -137
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
            #######
            yield env.timeout(node.packet.rectime + float(node.packet.proptime[math.ceil(env.now)])) ##GIVE TIME TO RECEIVE BEACON
                          
            if node in packetsAtBS:
                print ("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[12 - 7, [125,250,500].index(node.packet.bw) + 1]
                if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.header.lost = False
                    node.intraPacket.lost = False
                    trySend = False
                    nIntraPackets = 0
                else:
                    selectDR_er(env,node)
                    nodesToSend.append(node.nodeid)
                    wait = random.uniform(1,back_off - node.packet.rectime - float(node.packet.proptime[math.ceil(env.now)])) ##TRIGGER BACK-OFF TIME
                    yield env.timeout(wait)
                    #print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    trySend = True
                    node.sent = node.sent + 1
                    node.buffer = node.buffer - node.packetlen
                    if node in packetsAtBS:
                        print ("{} || ERROR: packet is already in...".format(env.now))
                    else:
                        #sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        sensibility = node.sensi
                        #print ("------Sensi is: ",sensibility)
                        if node.packet.rssi[math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                            print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                            node.header.lost = True ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = True ## LOST ONLY CONSIDERING Lpl
                            #nIntraPackets = 0
                            print ("###############lost !!!!!!!!")
                        else:
                            node.header.lost = False ## LOST ONLY CONSIDERING Lpl
                            node.intraPacket.lost = False ## LOST ONLY CONSIDERING Lpl
                            #print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                            #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                           
                        for i in range(len(node.header.freqHopHeader)):
                            ###print ("{:3.5f} || Sending Header replica {} node {}...".format(env.now,i,node.nodeid))
                            ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                            node.header.subCh = node.header.freqHopHeader[i]
                            #print ("SUBCHANELLLL: ",node.header.subCh)
                            node.header.sentIntra +=1
                            isLost =0
                            if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                node.header.Nlost +=1
                                isLost =1
                            if (checkcollision(node.header, packetsAtBS, maxBSReceives,env)==1):
                                #pass
                                if node.header.col == 1:
                                    if isLost == 0:
                                        node.header.collided +=1
                                #node.packet.collided = 1
                                #print ("---{:3.5f} || Collision for Header replica {} node {} !!!".format(env.now,i,node.nodeid))
                                #node.packet.collided = 1
                                #node.header.collided +=1 #ALREADY COUNTED IN FUNCTION                                
                            else:
                                ###print ("{:3.5f} || ...No Collision for Header replica {} node {}!".format(env.now,i,node.nodeid))
                                #node.packet.collided = 0
                                node.header.noCollided = 1 ##ALMOST ONE HEADER IS OK, THEN HEADER IS OK
                            packetsAtBS.append(node)
                            node.packet.addTime = env.now
                            isLost =0
                            yield env.timeout(node.header.rectime)
                            if (node in packetsAtBS):
                                packetsAtBS.remove(node)
                        
                        ##CALCULATE N OF INTRAPACKETS BASED ON PACKETLEN
                        #airtime(12,1,node.packetlen,125)
                        if node.dr == 8 or node.dr == 10:
                            payloadTime = 1.85 - 0.233*3 
                        elif node.dr == 9 or node.dr ==11:
                            payloadTime = 1.07 - 0.233*2
                            
                        nIntraPackets = math.ceil(payloadTime / 50e-3)
                        #print ("NUMBER OF INTRA PACKETSSSS",nIntraPackets)
                        
                        for j in range (nIntraPackets):
                            ###print ("{:3.5f} || Sending intra-packet {} of {} for node {}...".format(env.now,j,nIntraPackets-1,node.nodeid))
                            ###print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                            node.intraPacket.subCh = node.intraPacket.freqHopIntraPacket[j]
                            node.intraPacket.sentIntra +=1
                            isLost =0
                            if node.packet.rssi[math.ceil(env.now)] < sensibility:
                                node.intraPacket.Nlost +=1
                                isLost =1
                            #print ("INTRA-PACKT SUB CHANNELLLL", node.intraPacket.subCh)
                            if (checkcollision(node.intraPacket, packetsAtBS, maxBSReceives,env)==1):
                                #pass
                                if node.intraPacket.col ==1:
                                    if isLost == 0:
                                        node.intraPacket.collided+=1
                                #print ("---{:3.5f} || Collision for intra-packet {} for node {} !!!".format(env.now,j,node.nodeid))
                                #node.intraPacket.collided+=1 #ALREADY COUNTED ON FUNCTION
                            else:
                                ###print ("{:3.5f} || ...No Collision for intra-packet {} for node {}!".format(env.now,j,node.nodeid))
                                node.intraPacket.noCollided +=1
                                pass
                            packetsAtBS.append(node)
                            node.packet.addTime = env.now
                            yield env.timeout(node.intraPacket.rectime)
                            if (node in packetsAtBS):
                                packetsAtBS.remove(node)
                            #print ("INTRA-PACKET NO-PROCESEDDD",node.intraPacket.noProcessed)
                            isLost =0
            
            node.header.noCollided = len(node.header.freqHopHeader)-node.header.Nlost-node.header.collided
            node.intraPacket.noCollided = nIntraPackets-node.intraPacket.Nlost-node.intraPacket.collided
            
            if node.header.noCollided <0:
                node.header.noCollided = 0
            if node.intraPacket.noCollided <0:
                node.intraPacket.noCollided = 0
                
            if trySend == 1:
                #print ("----count intra-packet collided", node.intraPacket.collided)
                if node.header.lost or node.intraPacket.lost:
                    logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                else:
                    if node.dr ==8 or node.dr==10:
                        if node.header.collided == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 3:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (1/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                                   
                    elif node.dr==9 or node.dr==11:
                        if node.header.collided == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCh,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.collided > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PCp,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.header.noProcessed == 2:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        elif node.intraPacket.noProcessed > (2/3)*nIntraPackets:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
                        else:
                            logs.append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,#{},#{},#{},#{}".format(env.now,node.nodeid,node.dist[math.ceil(env.now)],node.elev[math.ceil(env.now)],node.dr,nIntraPackets,node.intraPacket.noCollided,len(node.header.freqHopHeader),node.header.noCollided))
            
            ##RESET
            node.header.collided = 0
            node.header.processed = 0
            node.header.noProcessed = 0
            node.header.lost = False
            node.header.noCollided =0
            node.intraPacket.nrColl = 0
            node.intraPacket.collided = 0
            node.intraPacket.processed = 0
            node.intraPacket.noProcessed = 0
            node.intraPacket.lost = False
            node.intraPacket.noCollided = 0
            node.header.sentIntra = 0
            node.intraPacket.sentIntra = 0
            node.header.Nlost =0
            node.intraPacket.Nlost = 0
            
            if trySend:
                #print ("BEACON TIMEEE",beacon_time)
                #print ("WAITTT",wait)
                #print ("NODE HEADER TIME",node.header.rectime)
                #print ("ONE INTRA-PACKET TIMEE",node.intraPacket.rectime)
                #yield env.timeout(beacon_time-wait)
                yield env.timeout(beacon_time-wait-2*3*node.header.rectime-2*nIntraPackets*node.intraPacket.rectime)
            else:
                nIntraPackets = 0
                yield env.timeout(beacon_time-wait-3*node.header.rectime-nIntraPackets*node.intraPacket.rectime)

    def selectDR_er (env,node):
        global DR
        dr = [8,9,10,11]
        node.dr = random.choice(dr)
        node.header.dr = node.dr
        node.intraPacket.dr = node.dr
        if node.dr == 11:
            node.sensi = DR[3]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
        elif node.dr == 10:
            node.sensi = DR[2]
            carriers = list(range(688))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:86]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]
        elif node.dr == 9:
            node.sensi = DR[1]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:2]
            node.intraPacket.freqHopIntraPacket = node.freqHop [2:]
        else:
            node.sensi = DR[0]
            carriers = list(range(280))
            random.shuffle(carriers) #TO CHOOSE THE HOPPING JUMPS
            node.freqHop = carriers[0:35]
            node.header.freqHopHeader = node.freqHop[0:3]
            node.intraPacket.freqHopIntraPacket = node.freqHop [3:]

    def beacon (env):
        global beacon_time
        global nodesToSend
        global beacon_rec
        i = 0
        while True:
            if i == 0:
                yield env.timeout(0)           
            else:
                yield env.timeout(beacon_time-2)
            i=i+1
            print ("{:3.5f} || ***A new beacon has been sended from Satellite***".format(env.now))
            beacon_rec =0
            yield env.timeout(2)
            logs.append("{:3.3f},B,{}".format(env.now,nodesToSend))
            nodesToSend = []       
                  



    #criar thread passar 


    env = simpy.Environment()

    env.process(beacon(env)) ##BEACON SENDER
    
    ### THIS IS GOING TO CREATE NODES AND DO TRAMSMISIONS. IS THE MAIN PROGRAM ###
    for i in range(nrNodes):
        #TODO colocar aqui a alteracao de qual esta sendo executado
        if sim_type == 'eb':
            env.process(transmit_eb(env,nodes[i],0,RANDOM_SEED))
        
        
        
        elif sim_type == 'etr':
            env.process(transmit_etr(env,node))
        elif sim_type == 'etbr':
            env.process(transmit_etbr(env,node))
        elif sim_type == 'etb':
            env.process(transmit_etb(env,node))
        elif sim_type == 'er':
            env.process(transmit_er(env,node))
        elif sim_type == 'et':
            env.process(transmit_et(env,node))


    env.run(until=600*2)

    for sat in range(num_sat):

        sent = sum(n.sent[sat] for n in nodes)

        folder = '../resultados/'+sim_type+'_3CH_s'+str(RANDOM_SEED)+'_p'+str(packetsToSend)+"_NOVO"
        if not os.path.exists(folder):
            os.makedirs(folder)
        fname = "./"+folder+"/" + str(sim_type+"_"+str(nrNodes)+"_3CH_"+str(maxBSReceives)+"_s"+str(RANDOM_SEED)+"_p"+str(packetsToSend)) + "SAT"+str(sat)+ ".csv"
        with open(fname,"w") as myfile:
            myfile.write("\n".join(logs[sat]))
        myfile.close()
        i=i+1
        if not mode_debbug:
            nodes = [] ###EACH NODE WILL BE APPENDED TO THIS VARIABLE
        print(fname)

    return ([sent,nrCollFullPacket,None,None,nrReceived],logs)



#########################################################################
if chan ==3:
    ###SCENARIO 3 CHANNELS###
    channel = [0,1,2]
    nodes = [] ###EACH NODE WILL BE APPENDED TO THIS VARIABLE
    nrLost = 0 ### TOTAL OF LOST PACKETS DUE Lpl
    nrCollisions = 0 ##TOTAL OF COLLIDED PACKETS
    nrProcessed = 0 ##TOTAL OF PROCESSED PACKETS
    nrReceived = 0 ###TOTAL OF RECEIVED PACKETS
    nrNoProcessed = 0 ##TOTAL OF INTRA-PACKETS NO PROCESSED
    nrIntraTot = 0
    nrLostMaxRec = 0
    nrCollFullPacket = 0
    nrSentIntra = 0 ##TOTAL OF SENT INTRA-PACKTES
    nrReceivedIntra = 0 ##TOTAL OF RECEIVED INTRA-PACKETS
    i =0
    
    for nrNodes in multi_nodes:
        print ("\n\n***NEW SCENARIO BEGINS***\n")
        simulate_scenario(nrNodes, sim_type)


if not mode_debbug:
    sys.stdout = old_stdout
    print("done ",sim_type)





