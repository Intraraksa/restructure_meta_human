# Text2Mouth Module (Draft)
ใช้ในงาน Meta Human ทำหน้าทีเล่นไฟล์เสียงที่ที่ถูก Generate ขึ้นมาจาก Botnoi API แล้วส่ง TimeStamp เพื่อ Matching กับการขยับปากของ Model

## การเรียกใช้งาน Module
``````````
from text2mouth_module import Text2MouthShape

t2m = Text2MouthShape()

t2m.msg_txt2blendshape('บันทึกรายการเรียบร้อยกรุณาพบแพทย์ที่ห้องศัลยกรรมกระดูกค่ะ') #รับค่าเป็น Text File
``````````
## Default Configulation
1. url="https://tts.botnoi.ai/api/doctts?text="
2. voice_type_1="",
3. voice_type_2="&speaker=tonkhaow"
4. max_len1=300-1
5. max_len2=200-1
6. model="tha20210309v2

## การใช้งาน Model allosaurus
1. สร้าง env **ในที่นี้ทดสอบจาก Anaconda
2. pip install allosaurus
3. นำโมเดล tha20210309v2 ไปไว้ใน side package


