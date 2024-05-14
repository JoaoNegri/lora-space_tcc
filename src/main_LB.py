import math
import os
import random
import sys
from time import sleep

import numpy as np
import simpy

from aux import checkcollision_LORA
from Node import Node

mode_debbug = 0

beacon_rec = 0
max_rec = 15

# if not mode_debbug:
#     null = open(os.devnull, 'w')
#     old_stdout = sys.stdout
#     sys.stdout = null
### WE START BY USING SF=12 ADN BW=125 AND CR=1, FOR ALL NODES AND ALL TRANSMISIONS######

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
    packetlen = int(sys.argv[3])  # NODES SEND PACKETS OF JUST 20 Bytes
    # TOTAL DATA ON BUFFER, FOR EACH NODE (IT'S THE BUFFER O DATA BEFORE START SENDING)
    total_data = int(sys.argv[4])
    beacon_time = int(sys.argv[5])  # SAT SENDS BEACON EVERY CERTAIN TIME
    # MAX NUMBER OF PACKETS THAT BS (ie SATELLITE) CAN RECEIVE AT SAME TIME
    maxBSReceives = int(sys.argv[6])

    # multi_nodes = [int(sys.argv[7]), int(sys.argv[8]) ,int(sys.argv[9])]
    multi_nodes = [int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9]), int(sys.argv[10]), int(sys.argv[11]), int(sys.argv[12]), int(
        sys.argv[13]), int(sys.argv[14]), int(sys.argv[15]), int(sys.argv[16]), int(sys.argv[17]), int(sys.argv[18]), int(sys.argv[19]), int(sys.argv[20])]
    p_skip_param = int(sys.argv[21])

    sim_type = sys.argv[22]
nodesToSend = [[], []]
packetsToSend = math.ceil(total_data/packetlen)
### GLOBAL PARAMS ####
bsId = 1  # ID OF BASE STATION (NOT USED)

avgSendTime = 3  # NOT USED! --> A NODE SENDS A PACKET EVERY X SECS

back_off = beacon_time * 0.95  # BACK OFF TIME FOR SEND A PACKET
c = 299792.458  # SPEED LIGHT [km/s]
Ptx = 14
G_device = 0  # ANTENNA GAIN FOR AN END-DEVICE
G_sat = 12  # ANTENNA GAIN FOR SATELLITE
nodes = []  # EACH NODE WILL BE APPENDED TO THIS VARIABLE
freq = 868e6  # USED FOR PATH LOSS CALCULATION
# FROM LORAWAN REGIONAL PARAMETERS EU863-870 / EU868
frequency = [868100000, 868300000, 868500000]


nrLost = 0  # TOTAL OF LOST PACKETS DUE Lpl
nrCollisions = 0  # TOTAL OF COLLIDED PACKETS
nrProcessed = 0  # TOTAL OF PROCESSED PACKETS
nrReceived = 0  # TOTAL OF RECEIVED PACKETS
nrNoProcessed = 0  # TOTAL OF INTRA-PACKETS NO PROCESSED
nrIntraTot = 0
nrLostMaxRec = 0
nrCollFullPacket = 0
nrSentIntra = 0  # TOTAL OF SENT INTRA-PACKTES
nrReceivedIntra = 0  # TOTAL OF RECEIVED INTRA-PACKETS


# ARRAY WITH MEASURED VALUES FOR SENSIBILITY, NEW VALUES
# THE FOLLOWING VALUES CORRESPOND TO:
#   - FIRST ELEMENT: IT'S THE SF (NOT USABLE)
#   - SECOND ELEMENT: SENSIBILITY FOR 125KHZ BW
#   - THIRD ELEMENT: SENSIBILITY FOR 250KHZ BW
#   - FOURTH ELEMENT: SENSIBILITY FOR 500KHZ BW
# NOTICE THAT SENSIBILITY DECREASE ALONG BW INCREASES, ALSO WITH LOWER SF
# THIS VALUES RESPONDS TO:
# wf = -174 + 10 log(BW) +NF +SNRf
sf7 = np.array([7, -123, -120, -117.0])
sf8 = np.array([8, -126, -123, -120.0])
sf9 = np.array([9, -129, -126, -123.0])
sf10 = np.array([10, -132, -129, -126.0])
sf11 = np.array([11, -134.53, -131.52, -128.51])
sf12 = np.array([12, -137, -134, -131.0])

sensi = np.array([sf7, sf8, sf9, sf10, sf11, sf12])

# DR = ["dr8","dr9","dr10","dr11"]
DR = [-137, -134.5, -134, -131.5]

## READ PARAMS FROM DIRECTORY ##
path = "../params/wider_scenario_2/"

### -137dB IS THE MINIMUN TOLERABLE SENSIBILITY, FOR SF=12 AND BW=125KHz ###

leo_pos = [np.loadtxt(path + "LEO-XYZ-Pos_sat1.csv", skiprows=1, delimiter=',', usecols=(1, 2, 3)),
           np.loadtxt(path + "LEO-XYZ-Pos_sat2.csv", skiprows=1, delimiter=',', usecols=(1, 2, 3))]
# WHERE:
# leo_pos[i,j]:
# i --> the step time in sat pass
# j --> 0 for x-position, 1 for y-position, 2 for z-position
num_sat = len(leo_pos)

sites_pos = np.loadtxt(path + "SITES-XYZ-Pos.csv",
                       skiprows=1, delimiter=',', usecols=(1, 2, 3))
# WHERE:
# sites_pos[i,j]:
# i --> the node i
# j --> 0 for x-position, 1 for y-position, 2 for z-position

dist_sat = np.zeros((sites_pos.shape[0], len(leo_pos), 3, leo_pos[0].shape[0]))
t = 0
for i in range(leo_pos[0].shape[0]):
    t += 1
    for j in range(len(leo_pos)):
        dist_sat[:, j, :, i] = leo_pos[j][i, :] - sites_pos
# WHERE:
    # dist_sat[i,j,k,l]:
        # i --> the node i
        # j --> the sat j
        # k --> 0 for x-position, 1 for y-position, 2 for z-position
        # l --> the step time in sat pass

#### FOR COMPUTE DISTANCE MAGNITUDE (ABS) FROM END-DEVICE TO SAT PASSING BY ####
distance = np.zeros((sites_pos.shape[0], len(leo_pos), leo_pos[0].shape[0]))
for j in range(len(leo_pos)):
    distance[:, j, :] = (dist_sat[:, j, 0, :]**2 +
                         dist_sat[:, j, 1, :]**2 + dist_sat[:, j, 2, :]**2)**(1/2)
# TODO ALTERAR O VALOR NO SAT1 e SAT2 para quando estiver fora de alcance não ser 0,0,0 e sim algo bemmmm mais distante
# WHERE:
    # distance[i,j,k]:
    # i --> the node i
    # j --> the sat j
    # k --> the step time in sat pass


## MATRIX FOR LINK BUDGET, USING Prx ###
Prx = np.zeros((sites_pos.shape[0], len(leo_pos), leo_pos[0].shape[0]))
# DISTANCE IS CONVERTED TO METERS
Prx: np.ndarray = Ptx + G_sat + G_device - 20 * \
    np.log10(distance*1000) - 20*np.log10(freq) + 147.55
# WHERE:
# Prx[i,j,k]:
# i --> the node i
# j --> the sat j
# k --> the step time in sat pass
packetsAtBS = []  # USED FOR CHEK IF THERE ARE ALREADY PACKETS ON THE SATELLITE
for _ in range(num_sat):
    packetsAtBS.append([])


elev = np.degrees(np.arcsin(599/distance))


def simulate_scenario(nrNodes, sim_type):
    # RANDOM SEED IS FOR GENERATE ALWAYS THE SAME RANDOM NUMBERS (ie SAME RESULTS OF SIMULATION)
    random.seed(RANDOM_SEED)
    nodes = []  # EACH NODE WILL BE APPENDED TO THIS VARIABLE
    logs = []
    for sat in range(num_sat):
        logs.append([])

    for i in range(nrNodes):
        node = Node(i, bsId, avgSendTime, packetlen, total_data,
                    distance, elev, channel, Ptx, Prx, frequency, num_sat, type='Legacy')
        nodes.append(node)

    def transmit_lb(env: simpy.Environment, node: Node, sat: int, random: random.Random):
        # while nodes[node.nodeid].buffer > 0.0:
        while node.buffer[sat] > 0.0:
            time = distance[node.nodeid % len(
                distance), :, math.ceil(env.now)]*(1/299792.458)

            first_wait = min(time)

            # decide se vai transmitir com base no satélite mais próximo
            yield env.timeout(node.packet.rectime + float(first_wait))

            if node in packetsAtBS[sat]:
                print("{:3.5f} || ERROR: packet is already in...".format(env.now))
            else:
                sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]

                aux_prx = Prx[node.nodeid %
                              len(distance), :, math.ceil(env.now)]

                max_prx = aux_prx.argmax()

                # caso nem o satélite mais próximo não seja capaz de receber (teoricamente),  não envia
                if aux_prx[max_prx] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                    print ("{:3.5f} || Node {}: Can not reach beacon due Lpl1".format(env.now,node.nodeid))
                    wait =0 ##LETS WAIT FOR NEXT BEACON
                    node.packet.lost[sat] = False
                    trySend = False
                    print(node.nodeid)
                    # while True: pass
                else:
                    nodesToSend[0].append(node.nodeid)
                    wait = random.uniform(2, back_off) - node.packet.rectime
                    yield env.timeout(wait)
                    logs[sat].append("trysend {} ==> {:3.3f}".format(node.nodeid,env.now))
                    print ("{:3.5f} || Node {} begins to transmit a packet".format(env.now,node.nodeid))
                    
                    yield env.timeout(distance[node.nodeid % len(distance), sat, math.ceil(env.now)]*(1/299792.458))

                    trySend = True
                    node.sent = node.sent + 1
                    node.buffer[sat] = node.buffer[sat] - node.packetlen
                    if node in packetsAtBS[sat]:
                        print("{} || ERROR: packet is already in...".format(env.now))
                    else:
                        sensibility = sensi[node.packet.sf - 7, [125,250,500].index(node.packet.bw) + 1]
                        if Prx[node.nodeid % len(distance), sat, math.ceil(env.now)] < sensibility: #HERE WE ARE CONSIDERING RSSI AT TIME ENV.NOW
                            print ("{:3.5f} || Node {}: The Packet will be Lost due Lpl".format(env.now,node.nodeid))
                            node.packet.lost[sat] = True ## LOST ONLY CONSIDERING Lpl
                            #necessário aguardar o tempo de transmissão mesmo quando o pacote é perdido
                            yield env.timeout(node.packet.rectime)
                        else:
                            node.packet.lost[sat] = False ## LOST ONLY CONSIDERING Lpl
                            # print ("{:3.5f} || Prx for node {} is {:3.2f} dB".format(env.now, node.nodeid, node.packet.rssi[math.ceil(env.now)]))
                            # #print ("Prx for node",node.nodeid, "is: ",node.packet.rssi[math.ceil(env.now)],"at time",env.now)
                            # print ("{:3.5f} || Let's try if there are collisions...".format(env.now))
                            if (checkcollision_LORA(node.packet,packetsAtBS[sat], maxBSReceives, sat,Prx , env)==1):
                                node.packet.collided[sat] = 1
                            else:
                                node.packet.collided[sat] = 0
                                print ("{:3.5f} || ...No Collision by now!".format(env.now))
                            packetsAtBS[sat].append(node)
                            node.packet.addTime = env.now
                            yield env.timeout(node.packet.rectime)
            
            if trySend == 1:
                if node.packet.lost[sat]:
                    print ("{:3.5f} || Node {} ended to transmit a packet".format(env.now,node.nodeid))

                    logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PL,{}".format(env.now,node.nodeid,distance[node.nodeid % len(distance)][sat, math.ceil(env.now)],0,node.packet.sf,node.buffer[sat]/20))
                elif node.packet.collided[sat]:
                    logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PC,{}".format(env.now,node.nodeid,distance[node.nodeid % len(distance)][sat, math.ceil(env.now)],0,node.packet.sf,node.buffer[sat]/20))
                elif node.packet.processed[sat] == 0:
                    logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},NP,{}".format(env.now,node.nodeid,distance[node.nodeid % len(distance)][sat, math.ceil(env.now)],0,node.packet.sf,node.buffer[sat]/20))
                else:
                    print ("{:3.5f} || Node {} ended to transmit a packet".format(env.now,node.nodeid))
                    logs[sat].append("{:3.3f},{},{:3.3f},{:3.3f},{},PE,{}".format(env.now,node.nodeid,distance[node.nodeid % len(distance)][sat, math.ceil(env.now)],0,node.packet.sf,node.buffer[sat]/20))
            
            # complete packet has been received by base station
            # Let's remove from Base Station
            if (node in packetsAtBS[sat]):
                packetsAtBS[sat].remove(node)
                # reset the packet
            node.packet.collided[sat] = [0]
            node.packet.processed[sat] = [0]
            node.packet.lost[sat] = [False]
            
            #yield env.timeout(beacon_time-wait-node.packet.rectime)

            if trySend:
                print('will wait now :', beacon_time-wait-2*node.packet.rectime  )
                yield env.timeout(beacon_time-wait-(2*node.packet.rectime)- distance[node.nodeid % len(distance), sat, math.ceil(env.now)]*(1/299792.458))
            else:
                # print(node.nodeid)
                # print(env.now)
                # print(beacon_time-wait-node.packet.rectime)
                # print("Next event will occur at time", env.peek())
                yield env.timeout(beacon_time-wait-(node.packet.rectime))
        
    def beacon(env):
        global beacon_time
        global beacon_rec
        i = 0
        while True:
            if i == 0:
                yield env.timeout(0)
            else:
                yield env.timeout(beacon_time-2)
            i = i+1
            print(
                "{:3.5f} || ***A new beacon has been sended from Satellite***".format(env.now))
            beacon_rec = 0
            print(f'beacon next event {env.peek()}')
            yield env.timeout(2)
            # logs[0].append("{:3.3f},B,{}".format(env.now,nodesToSend[0]))
            nodesToSend[0] = []

    # criar thread passar
    ### THIS IS GOING TO CREATE NODES AND DO TRAMSMISIONS. IS THE MAIN PROGRAM ###
    randons = []
    z = 0
    for sat in range(num_sat):

        env = simpy.Environment()

        env.process(beacon(env))  # BEACON SENDER
        randons.append(random.Random(RANDOM_SEED))
        for i in range(nrNodes):
            if sim_type == 'lb':
                print(env.now)
                env.process(transmit_lb(env, nodes[i], sat, randons[sat]))


        env.run(until=600*4)

        folder = '../resultados/'+sim_type+'_3CH_s' + \
            str(RANDOM_SEED)+'_p'+str(packetsToSend)+"_NOVO"
        if not os.path.exists(folder):
            os.makedirs(folder)
        fname = "./"+folder+"/" + str(sim_type+"_"+str(nrNodes)+"_3CH_"+str(
            maxBSReceives)+"_s"+str(RANDOM_SEED)+"_p"+str(packetsToSend)) + "SAT"+str(sat) + ".csv"
        with open(fname, "w") as myfile:
            myfile.write("\n".join(logs[sat]))
        myfile.close()
        i = i+1

        print(fname)
        z += 1
    return ([nrCollFullPacket, None, None, nrReceived], logs)


#########################################################################
if chan == 3:
    ### SCENARIO 3 CHANNELS###
    channel = [0, 1, 2]
    nodes = []  # EACH NODE WILL BE APPENDED TO THIS VARIABLE
    nrLost = 0  # TOTAL OF LOST PACKETS DUE Lpl
    nrCollisions = 0  # TOTAL OF COLLIDED PACKETS
    nrProcessed = 0  # TOTAL OF PROCESSED PACKETS
    nrReceived = 0  # TOTAL OF RECEIVED PACKETS
    nrNoProcessed = 0  # TOTAL OF INTRA-PACKETS NO PROCESSED
    nrIntraTot = 0
    nrLostMaxRec = 0
    nrCollFullPacket = 0
    nrSentIntra = 0  # TOTAL OF SENT INTRA-PACKTES
    nrReceivedIntra = 0  # TOTAL OF RECEIVED INTRA-PACKETS
    i = 0

    for nrNodes in multi_nodes:
        print("\n\n***NEW SCENARIO BEGINS***\n")
        simulate_scenario(nrNodes, sim_type)


if not mode_debbug:
    sys.stdout = old_stdout
    print("done ", sim_type)
