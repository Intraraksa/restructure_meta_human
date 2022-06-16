# import onnx
import onnxruntime
from scipy.io import wavfile
import scipy.signal as sps 
import sounddevice as sd
import numpy as np
from pythainlp.util import normalize
from datetime import datetime
# from utils import model_onnx


ort_session = onnxruntime.InferenceSession('model/asr_botnoi.onnx')

with open("model/vocab.json","r",encoding="utf-8-sig") as f:
    d = eval(f.read())

res = dict((v,k) for k,v in d.items())
res[69]="[PAD]"
res[68]="[UNK]"

class ASR():
    def __init__(self,audio_maxlen=100000,new_rate=16000):
        self.audio_maxlen = audio_maxlen
        self.new_rate = new_rate

    def _normalize(self,x): #
        """You must call this before padding.
    Code from https://github.com/vasudevgupta7/gsoc-wav2vec2/blob/main/src/wav2vec2/processor.py#L101
    Fork TF to numpy
    """
    # -> (1, seqlen)
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        # return np.squeeze((x - mean) / np.sqrt(var + 1e-5))
        res  =  np.squeeze((x - mean) / np.sqrt(var + 1e-5)) 
        mean = None
        var  = None
        return res

    def remove_adjacent(self,item): # code from https://stackoverflow.com/a/3460423
        nums = list(item)
        a = nums[:1]
        for item in nums[1:]:
            if item != a[-1]:
                a.append(item)

        nums = None
        return ''.join(a)

    def asr(self,path,freq=44100):
        """
        Code from https://github.com/vasudevgupta7/gsoc-wav2vec2/blob/main/notebooks/wav2vec2_onnx.ipynb
        Fork TF to numpy
        """
        if path.split(".")[1] == "wav":
            sampling_rate, data = wavfile.read(path)
            samples = round(len(data) * float(self.new_rate) / freq)
            new_data = sps.resample(data, samples)
        else:    
            # sampling_rate, data = wavfile.read(path)
            samples = round(len(path) * float(self.new_rate) / freq)
            # new_data = sps.resample(np.squeeze(recording,1), samples)
            new_data = sps.resample(np.squeeze(path,1), samples)
        samples = None
        speech = np.array(new_data, dtype=np.float32)
        new_data = None
        speech = self._normalize(speech)[None]
        padding = np.zeros((speech.shape[0], self.audio_maxlen - speech.shape[1]))
        speech = np.concatenate([speech, padding], axis=-1).astype(np.float32)
        ort_inputs = {"modelInput": speech}
        speech =  None
        start = datetime.now()
        ort_outs = ort_session.run(None, ort_inputs)
        end = datetime.now()
        print(end-start)
        prediction = np.argmax(ort_outs, axis=-1)
        ort_inputs =  None
        ort_outs = None
        # Text post processing
        _t1 = ''.join([res[i] for i in list(prediction[0][0])])
        prediction = None
        return normalize(''.join([self.remove_adjacent(j) for j in _t1.split("[PAD]")]))




