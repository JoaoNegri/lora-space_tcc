import numpy as np
class Header ():
    def __init__(self ,nodeid: int, dist: np.ndarray[int, np.float64], ch: int, freqHop: list[int],
    dr: int, Prx: np.ndarray[int, np.float64], Ptx: int, distance: np.ndarray[int, np.float64]):
        global channel
        global frequency
        self.nodeid = nodeid
        self.txpow = Ptx
        self.transRange = 150
        self.arriveTime = 0
        self.rssi = Prx[nodeid%len(Prx),:,:]
        self.rectime = 0.233
        #self.rectime = 1.5
        c = 299792.458 ###SPEED LIGHT [km/s]


        self.proptime = distance[nodeid%len(distance),:,:]*(1/c)
        self.collided = 0
        self.noCollided = 0
        self.processed = 0
        self.noProcessed = 0
        self.ch = ch
        self.lost = bool
        self.Nlost = 0
        self.subCh = 0
        self.sentIntra = 0
        self.dr = dr
        self.col =0
        if dr == "dr8":
            self.freqHopHeader = freqHop[0:3]
        elif dr == "dr9":
            self.freqHopHeader = freqHop[0:2]
        elif dr == "dr10":
            self.freqHopHeader = freqHop[0:3]
        elif dr == "dr11":
            self.freqHopHeader = freqHop[0:2]