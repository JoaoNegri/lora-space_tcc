from Packet import Packet
class IntraPacket (Packet):
    def __init__(self,nodeid,dist,ch,freqHop, dr, Prx, Ptx, distance, packetlen, frequency):
        global channel

        super().__init__(nodeid, packetlen, dist, Ptx, Prx, frequency, distance)
        self.nodeid = nodeid
        self.txpow = Ptx
        self.transRange = 150
        self.arriveTime = 0
        self.freqHopIntraPacket = freqHop[3:]
        self.rectime = 50e-3
        #self.rectime = 3

        c = 299792.458 ###SPEED LIGHT [km/s]

        self.collided = 0
        self.noCollided = 0
        self.nrColl = 0
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
            self.freqHopIntraPacket = freqHop[3:]
        elif dr == "dr9":
            self.freqHopIntraPacket = freqHop[2:]
        elif dr == "dr10":
            self.freqHopIntraPacket = freqHop[3:]
        elif dr == "dr11":
            self.freqHopIntraPacket = freqHop[2:]