#This file is module file use for txt2mouthshape.py
import os
import numpy as np
import socketio
import requests
import re
import json
import librosa
import soundfile as sf
from allosaurus.app import read_recognizer
import pickle
import time
# import load_message

# set path
path_root = os.getcwd()
path_src = os.path.join(path_root, "src")
path_data = os.path.join(path_src, "data")
# url tts
url_1 = "https://voice.botnoi.ai/api/v1/f1/speak?text="
url_2 = "https://voice.botnoi.ai/api/tts?text="

def save_dict(fn, dat):
        with open(fn, 'wb') as handle:
            pickle.dump(dat, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_dict(fn):
    with open(fn, 'rb') as handle:
        dat = pickle.load(handle)
    return dat

voice_dict = load_dict(os.path.join(path_data, "nurse_voice_tk_dict.pkl"))
path_voice = os.path.join(path_src, "voice_tk")

class Text2MouthShape():
    ipa2bs_dict =   {
                    "a": "A", "aj": "A", "aː": "A", "a̯": "A", "b": "BMP", "d": "DNT", "e": "E", "eː": "E", "f": "FV", "h": "H", 
                    "i": "IJ", "ia̯": "IJ", "iː": "IJ", "iːa̯": "IJ", "j": "IJ", "k": "KG", "kʰ": "KG", "l": "L", "m": "BMP", "n": "DNT", 
                    "o": "O", "oː": "O", "p": "BMP", "pʰ": "BMP", "r": "R", "s": "SZ", "t": "DNT", "tʰ": "DNT" , "t͡ɕ": "DNT", "t͡ɕʰ": "DNT", 
                    "u": "UW", "ua̯": "UW", "uː": "UW", "uːa̯": "UW", "w": "UW", "ŋ": "KG", "ɔ": "C", "ɔː": "C", "ɛ": "3", "ɛː": "3", 
                    "ɤ": "3", "ɤː": "3", "ɯ": "3", "ɯa̯": "3", "ɯː": "3", "ɯːa̯": "3", "ʔ": "0", " ": "0"   
                }
    def __init__(self,url="https://tts.botnoi.ai/api/doctts?text=",voice_type_1="",voice_type_2="&speaker=tonkhaow",max_len1=300-1,max_len2=200-1,model="tha20210309v2"):
        self.url_2 = url
        self.voice_type_1 = voice_type_1
        self.voice_type_2 = voice_type_2
        self.max_len_tts_1 = max_len1
        self.max_len_tts_2 = max_len2
        # self.ipa2bs_dict = ipa2bs_dict
        self.model = read_recognizer(model)

    def check_voice(self,msg, path_voice):
        print(path_voice)
        voice_stat = False
        # countdown time
        timer_start = time.perf_counter()
        # select URL for TTS api
        if len(msg) > self.max_len_tts_2:
            url = url_1
            voice_type = self.voice_type_1
            msg = msg[:self.max_len_tts_1]
        else:
            url = url_2
            msg = msg[:self.max_len_tts_2]
            voice_type = self.voice_type_2
        
        # first download
        try:
            print(path_voice)
            r = requests.get(url+msg+voice_type, allow_redirects=True)
            open(os.path.join(path_voice), 'wb').write(r.content)
            print("saved audio")
        except Exception as e :
            print(e)
            print("download audio not finished")
        
        # loop check file and download voice file if file it not complete -> loop until countdown to zero
        while(not voice_stat):
            try:
                x, fs = sf.read(path_voice)
                print(fs)
                voice_stat = True
            except Exception as e:
                print(e)
                print(url+msg+voice_type)
                # check countdown time
                print(abs(timer_start - time.perf_counter()))
                if abs(timer_start - time.perf_counter()) > 10:
                    print(abs(timer_start - time.perf_counter()))
                    voice_stat = False
                    return voice_stat
                try:
                    r = requests.get(url+msg+voice_type, allow_redirects=True)
                    open(os.path.join(path_voice), 'wb').write(r.content)
                    print("saved audio")
                except Exception as e:
                    print(e)
                    print("download audio not finished")
        
        return voice_stat

    # clean text
    def clean_txt(self,txt):
        txt = re.sub('\s+',' ',txt)
        txt = txt.replace("||", " ")
        txt = txt.replace("/", "")
        txt = txt.replace("<", "")
        txt = txt.replace(">", "")
        txt = txt.replace("(", "")
        txt = txt.replace(")", "")
        txt = txt.replace("[", "")
        txt = txt.replace("]", "")
        txt = txt.replace("{", "")
        txt = txt.replace("}", "")
        return txt

    # pack ipa timestamp and voice_file_name to json 
    def get_json_speech(self,time_list,ipa_tok, voice_file):
        
        time_list = list(time_list)

        speech_dict = { "file": voice_file,  "Result": [ ]}

        for i in range(len(time_list)):
            ms_dict = {"ipa": ipa_tok[i], "timer": time_list[i]}
            speech_dict["Result"].append(ms_dict)
    
        return speech_dict


    # generate mouthshape with timestamp and save to json file
    def update_mouth_blendshape(self,msg, path_voice, voice_fn):
        
        # get voice file
        path_voice_file = os.path.join(path_voice, voice_fn)
        
        # find duration voice file
        sound, sr = librosa.load(path_voice_file, sr=44100)
        sound_duration = librosa.get_duration(sound, sr=sr)
        
        
        # run inference -> æ l u s ɔ ɹ s
        # get output and timestamp
        # output = "A B C . . . Z", timestamp = [ 0.1, 0.2, 0.3, . . ., 0.9 ]
        output, times = self.model.recognize(path_voice_file, 'tha')
        
        # split output string to list
        # "A B C . . . Z" -> ["A", "B", "C", . . ., "Z"]
        output = list(output.split(" "))
        
        # scale times output with duration
        # duration = 2, [ 0.1, 0.2, 0.3, . . ., 0.9 ] -> [ 0.2, 0.4, 0.6, . . ., 1.8]
        time_stamps = np.array(times)*sound_duration
        
        # use this condition for case output of model is null so need to generate some information to create json file
        if output == ['']:
            output = ["l"]
            time_stamps = np.asarray([1.0])
        
        # map ipa output to blendshape
        output_toks = [self.ipa2bs_dict[val] for val in output]
        
        # pack blendshape timestamp and voice_file_name to json
        json_temp = json.dumps(get_json_speech(time_stamps, output_toks, voice_fn))
        print(json_temp)
        print(path_voice_file)
        # write json file
        with open(path_voice_file.replace(".wav", ".json"), 'w') as f:
        # with open(path_voice_file.replace(".mp3", ".json"), 'w') as f:
            json.dump(json_temp, f, ensure_ascii=False)
    

    print(list(voice_dict.keys()))
    # print("load landmark")

    # generate voice and json mouthshape file function
    def txt2blendshape(self,msg, end_flow):
        
        # clean message
        msg = self.clean_txt(msg)
        # if message not in voice_dict -> generate voice and json mouthshape file
        if msg not in list(voice_dict.keys()):  
            # clean a-zA-z english alphabet for TTS api
            msg = re.sub(r"[a-zA-Z]",'', msg)
            # trim space, " characters " -> "characters"
            msg = msg.strip()
            # convert null or space message ("    ") to some word
            if msg == "" or msg.isspace():
                msg = "อืม"
                
            # download voice file and check status download is success or not
            check_voice_para = self.check_voice(msg, os.path.join(path_voice, "nurse_"+str(len(list(voice_dict.keys())))+'.wav'))
            # check_voice_para = self.check_voice(msg, os.path.join(path_voice, "nurse_"+str(len(list(voice_dict.keys())))+'.mp3'))
            # if download voice is not success it will be trigger open speech recog for get next input 
            if not check_voice_para :
                check_data = 'no'
                # send to "forceMic_TurnOn" in Unity
                # sio.emit("rev_forceMic_TurnOn", check_data) 
                return check_voice_para
            print("- - - saved new audio - - -")
            
            # add message to voice_dict
            voice_dict[msg] = "nurse_"+str(len(list(voice_dict.keys())))+'.wav'
            # voice_dict[msg] = "nurse_"+str(len(list(voice_dict.keys())))+'.mp3'
            # generate and save mouthshape json file
            self.update_mouth_blendshape(msg, path_voice, voice_dict[msg])
            
            # save lasted voice_dict
            print("Done")
            save_dict(os.path.join(path_src, "data", "nurse_voice_tk_dict.pkl"), voice_dict)
            
        # check file again
        self.check_file(msg, path_voice)
        print("have file")
        # load json mouthshape file
        with open(os.path.join(path_voice, voice_dict[msg].replace(".wav", ".json"))) as json_file:
        # with open(os.path.join(path_voice, voice_dict[msg].replace(".mp3", ".json"))) as json_file:
            json_dict = json.load(json_file)
        print(json_dict)
        json_dat = json.dumps(json_dict)
        print(json_dat)
        
        # send json "recv_mouthshape" or "recv_mouthshape_end" to Unity

        ### Un comment บรรทัดนี้
        # if(end_flow):
        #     #not open next speech recog after speak
        #     sio.emit("send_mouthshape_end", json_dat) 
        # else:
        #     #open next speech recog after speak
        #     sio.emit("send_mouthshape", json_dat)
        ### ถึงบรรทัดนี้

        
    # check voice and mouthshape json file
    def check_file(self,msg, path_voice):
        # print(voice_dict[msg].replace(".wav", ".json"))
        # check is have voice file ?
        if not os.path.isfile(os.path.join(path_voice, voice_dict[msg])):
            self.check_voice(msg, os.path.join(path_voice, voice_dict[msg]))
            self.update_mouth_blendshape(msg, path_voice, voice_dict[msg])
        # check is have mouthshape json file ?
        elif not os.path.isfile(os.path.join(path_voice, voice_dict[msg].replace(".wav", ".json"))):
        # elif not os.path.isfile(os.path.join(path_voice, voice_dict[msg].replace(".mp3", ".json"))):
            self.update_mouth_blendshape(msg, path_voice, voice_dict[msg])

    # extract message -> txt2blendshape function
    def msg_txt2blendshape(self,msg):
        
        # check flow bot (check mic close or not) from keyword
        end_flow = False  
        if "กรุณาภาพ" in msg:
            msg = msg.replace("กรุณาภาพ ", "")
            end_flow = True
        if "กรุณา" in msg or "ออกจากการคุยเรียบร้อย" in msg:
            end_flow = True

        print(msg)
        # generate voice and json mouthshape file function
        self.txt2blendshape(msg, end_flow)
