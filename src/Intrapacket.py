import numpy as np
class IntraPacket ():
    
    c = 299792.458 ###SPEED LIGHT [km/s]

    def __init__(self, nodeid: int, ch: int, freqHop: list[int],
    dr: int, Prx: np.ndarray[int, np.float64], Ptx: int, distance: np.ndarray[int, np.float64], num_sat: int):
        self.nodeid = nodeid
        self.txpow = Ptx
        self.transRange = 150
        self.arriveTime = 0
        self.rectime = 50e-3
        #self.rectime = 3


        # self.proptime = distance[nodeid%len(distance),:,:]*(1/ 299792.458)
        
        self.freqHopIntraPacket = []
        self.subCh = []
        self.collided = []
        self.noCollided = []
        self.nrColl = []
        self.processed = []
        self.noProcessed = []
        self.lost = []
        self.Nlost = []
        self.sentIntra = []
        self.col = []
        for _ in range(num_sat):
            self.freqHopIntraPacket.append(freqHop[3:])
            self.subCh.append(0)
            self.collided.append(0)
            self.noCollided.append(0)
            self.nrColl.append(0)
            self.processed.append(0)
            self.noProcessed.append(0)
            self.lost.append(False)
            self.Nlost.append(0)
            self.sentIntra.append(0)
            self.col.append(0)

        self.dr = dr
        self.ch = ch