import numpy as np
import math
import cv2
import dlib
import os, shutil, subprocess
import time
import base64
from PIL import Image
from io import BytesIO
import pickle
import socketio

from keras.models import load_model
from fer import FER

from facedec_module import Face_dec

sio = socketio.Client()
face_dec = Face_dec()

@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')

# connect to socket server
sio.connect('http://localhost:8080')

# receive trigger to start send face image to unity
@sio.event
def recv_play_facereg(data):
    print('receive ', data)
    face_dec.chg_face_lock_stat(False)


# receive trigger to stop send face image to unity
@sio.event
def recv_stop_facereg(data):
    print('receive ', data)
    face_dec.chg_face_lock_stat(True)

@sio.event
def recv_start_rpy_(data):
    global param_check
    data = data.lower()
    if data == 'true':
        data = True
    else:
        data = False
    param_check = face_dec.change_param_check(data)

# Play opencv by webcam 
face_dec.playVideo(video_file=0)

# wait for receive socket
sio.wait()