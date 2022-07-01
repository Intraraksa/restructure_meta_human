
# -*- coding: utf-8 -*-
import os
import numpy as np
import socketio
import requests
import re
import json
import librosa
import soundfile as sf
import time
import pickle
from allosaurus.app import read_recognizer
from text2mouth_module import Text2MouthShape

# set path
# path_root = "C:/Users/titip/Desktop/Project_samutDownGrade_Build_V0.3/project_samut_Data/StreamingAssets/python/"
# path_root = "C:/Work/Botnoi/Project_samutDownGrade_Build_V0.3/project_samut_Data/StreamingAssets/python"
t2m = Text2MouthShape()
path_root = os.getcwd()
path_src = os.path.join(path_root, "src")

#create client socket
sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')

# get message to trigger speak -> msg_txt2blendshape function
@sio.event
def recv_speak(data):
    print('receive ', data)
    t2m.msg_txt2blendshape(data)
# connect to socket server
sio.connect('http://localhost:8080')      

# wait for receive socket
sio.wait()























