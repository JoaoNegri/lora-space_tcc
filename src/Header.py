import numpy as np
class Header ():
    
    c = 299792.458 ###SPEED LIGHT [km/s]
    
    def __init__(self ,nodeid: int, ch: int, freqHop: list[int],
    dr: int, Prx: np.ndarray[int, np.float64], Ptx: int, distance: np.ndarray[int, np.float64],num_sat: int):
        self.nodeid = nodeid
        self.txpow = Ptx
        self.transRange = 150
        self.arriveTime = 0
        self.rectime = 0.233
        #self.rectime = 1.5

        self.collided = []
        self.noCollided = []
        self.processed = []
        self.noProcessed = []
        self.Nlost = []
        self.subCh = []
        self.sentIntra = []
        self.col = []
        self.lost = []
        for _ in range(num_sat):

            self.collided.append(0)
            self.noCollided.append(0)
            self.processed.append(0)
            self.noProcessed.append(0)
            self.Nlost.append(0)
            self.subCh.append(0)
            self.sentIntra.append(0)
            self.col.append(0)
            self.lost.append(False)
        self.ch = ch
        self.dr = dr
        if dr == "dr8":
            self.freqHopHeader = freqHop[0:3]
        elif dr == "dr9":
            self.freqHopHeader = freqHop[0:2]
        elif dr == "dr10":
            self.freqHopHeader = freqHop[0:3]
        elif dr == "dr11":
            self.freqHopHeader = freqHop[0:2]