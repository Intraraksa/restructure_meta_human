import eventlet
import socketio
import speech_recognition as sr

recog = sr.Recognizer()

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def recive_msg(sid, data):
    print('message ', data)
    
@sio.event
def asr(sid , data): ## รับไฟล์ Path มาจาก Unity
    asr_func(data) ## เรียกใช้ ASR 

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    
def asr_func(data): ## Function แปลง Wavfile เป็น Text
    audio_file_ = sr.AudioFile(data)
    with audio_file_ as source:
        audio_file = recog.record(source, duration = 7.0)
        result = recog.recognize_google(audio_data=audio_file, language='th')
        # print(result)
        sio.emit("text2unity",result) ## ส่ง Text กลับไปหา Unity

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)