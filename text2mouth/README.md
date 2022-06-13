# Text2Mouth Module (Draft)
ใช้ในงาน Meta Human ทำหน้าทีเล่นไฟล์เสียงที่ที่ถูก Generate ขึ้นมาจาก Botnoi API แล้วส่ง TimeStamp เพื่อ Matching กับการขยับปากของ Model

## การเรียกใช้งาน Module
``````````
from text2mouth_module import Text2MouthShape

t2m = Text2MouthShape()

t2m.msg_txt2blendshape('บันทึกรายการเรียบร้อยกรุณาพบแพทย์ที่ห้องศัลยกรรมกระดูกค่ะ') #รับค่าเป็น Text File
``````````



