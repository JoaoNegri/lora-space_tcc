import numpy as np
class IntraPacket ():
    
    c = 299792.458 ###SPEED LIGHT [km/s]

    def __init__(self, nodeid: int, dist: np.ndarray[int, np.float64], ch: int, freqHop: list[int],
    dr: int, Prx: np.ndarray[int, np.float64], Ptx: int, distance: np.ndarray[int, np.float64], num_sat: int):
        self.nodeid = nodeid
        self.txpow = Ptx
        self.transRange = 150
        self.arriveTime = 0
        self.rssi = Prx[nodeid%len(Prx),:,:]
        self.freqHopIntraPacket = freqHop[3:]
        self.rectime = 50e-3
        #self.rectime = 3


        self.proptime = distance[nodeid%len(distance),:,:]*(1/IntraPacket.c)
        for _ in range(num_sat):

            self.collided = 0
            self.noCollided = 0
            self.nrColl = 0
            self.processed = 0
            self.noProcessed = 0
            self.lost = bool
            self.Nlost = 0
            self.subCh = 0
            self.sentIntra = 0
            self.col =0

        self.dr = dr
        self.ch = ch
        if dr == "dr8":
            self.freqHopIntraPacket = freqHop[3:]
        elif dr == "dr9":
            self.freqHopIntraPacket = freqHop[2:]
        elif dr == "dr10":
            self.freqHopIntraPacket = freqHop[3:]
        elif dr == "dr11":
            self.freqHopIntraPacket = freqHop[2:]