import socketio
import requests

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')
    send_path('C:/Users/n_int/Downloads/google_asr/google_asr/test.wav') ### ใส่ Path Wavefile ที่นี่

@sio.event
def my_message(data):
    print('message received with', data)
    sio.emit('recive_msg', {'response': data})
    
@sio.event
def send_path(data): ## ส่ง socket asr
    print("recieve path ", data)
    sio.emit('asr',data) #emit("ชื่อ socket ฝั่ง socket" , wavfile path)
    
@sio.event
def text2unity(data): ## รับ text กลับมาจาก asr เตรียมส่งเข้า chatbot
    print("text is : ", data)

@sio.event
def disconnect():
    print('disconnected from server')



sio.connect('http://localhost:5000')
sio.wait()