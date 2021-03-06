# ASR module

ASR Module ใช้สำหรับแปลงสัญญาณเสียงเป็นข้อมูลประเภท Text โดยที่ใช้ Model ASR ที่ถูกแปลงเป็น ONNX model

## Model conversion
การแปลง Model ASR จาก Huggingface model ทางผู้จัดทำได้ [Colab](https://github.com/Intraraksa/restructure_meta_human/blob/master/asr/project_asr2onnx.ipynb) สำหรับแปลง Model เป็น ONNX เอาไว้รวมถึงวิธีการ Inference ONNX model เอาไว้ และการ inference ได้ถูกทำเป็น Module class object เอาไว้เพื่อให้ใช้งานได้โดยง่าย

## การเรียกใช้งาน Module
1. อิมพอร์ตโมดูล
``````
from asr_module import ASR
``````
2. เรียกใช้งานโมดูลคลาส Object
``````
#Set audio_maxlen 100000 เป็น default
#Set new_rate = 16000 เป็น default
asr = ASR(audio_maxlen=100000,new_rate=16000)
``````
3. ป้อนไฟล์เสียงที่ต้องการจะ Inference 
** สามารถป้อนอินพุตเป็นไฟล์ .wav กับเสียงที่บันทึกผ่านไมล์ได้โดยตรง
โดยที่ในการทกลองบันทึกเสียงผ่านไมล์ใช้ Library sounddevice และบันทึกเป็น 1 channel

``````
asr.asr("output.wav",freq=44100) ##ป้อนอินพุตเป็น wav file ถ้าบันทึกแบบเปิดปิดไมค์ให้ใส่เป็นตัวแปลที่เก็บค่า array เสียง 
``````
