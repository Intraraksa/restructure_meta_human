# -*- coding: utf-8 -*-
import socketio
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes
from smartcard_module import SmartCard

# APDU key
# SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
# THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
# CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]

smartcard = SmartCard()

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')

# start scan card loop
@sio.event
def run_cid(data):
    print('receive ', data)
    smartcard.chg_search_stat(True)
    smartcard.scan_card()

# stop scan card loop
@sio.event
def stop_cid(data):
    print('receive ', data)
    smartcard.chg_search_stat(False)

sio.connect('http://localhost:8080') 

sio.wait()       
