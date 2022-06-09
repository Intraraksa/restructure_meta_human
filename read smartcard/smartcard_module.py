# This file is module file
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes

# APDU key
SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]

class SmartCard():
    search_cid = [False]

    def __init__(self,select=SELECT,national_card=THAI_CARD,cmd_cid=CMD_CID):
        self.select = select
        self.nation_card = national_card
        self.cmd_cid = cmd_cid

    def thai2unicode(self,data):
        #decode data
        result = bytes(data).decode('tis-620')
        return result.strip()

    def getData(self,connection,cmd, req = [0x00, 0xc0, 0x00, 0x00]):
        #getdata from smartcard
        data, sw1, sw2 = connection.transmit(cmd)
        data, sw1, sw2 = connection.transmit(req + [cmd[-1]])
        return [data, sw1, sw2]

    def checkstatus(self):
        try:
            r=readers()
            reader = r[0]
            connection = reader.createConnection()
            return True
        except:
            return False

    # change variable for control loop wait for scan card
    def chg_search_stat(self,search_stat):
        self.search_cid[0] = search_stat

    # read id_card
    def read_smartcard(self):
        try:
            r=readers()
            #print(r)
            reader = r[0]
            #print(reader)
            connection = reader.createConnection()
        except:
            print("device is not connected")
            return "error"
        try:
            connection.connect()
            data, sw1, sw2 = connection.transmit(self.select + self.nation_card)
            data = self.getData(connection,self.cmd_cid)
            cid = self.thai2unicode(data[0])
            #print ("CID: " + cid)
            if len(cid) != 13:
                return "not_cid"
            else:
                return str(cid)
        except Exception as e:
            error_str = str(e)
            #print(error_str)
            if "protocol" in error_str:
                return "incorrect" 
            else:
                return "error"

    # loop wait for scan card and return value to "recv_cid" in Unity
    def scan_card(self):
        while(self.search_cid[0]):
            cid = self.read_smartcard()
            print(str(cid))
            if len(cid) == 13 or cid == "not_cid" or cid == "incorrect":
                print(cid)
                self.search_cid[0] = False
                sio.emit("send_cid", cid)
                break
