# Face detection module 
เป็นไฟล์ที่ทำไว้แยกต่างหากจาก face detection client โดยแยกเป็นส่วน Module file กับ Client file

## วิธีการ import โมดูล 
```
from facedec_module import Facedec
```

## วิธีใช้งานโมดูล
```
face_dec = Face_dec()
```

## Play video with opencv
หลังจากเรียกใช้งาน Module แล้วสามารถสั่งให้ระบบ Play Video ด้วยคำสั่ง
```
face_dec.playVideo(video_file=0)
```

### Default configuration face detection module
1. weight_model = 'model_15frame_adddata.h5'
2. pickle_file = "src/rpy_tee.pickle"
3. mtcnn = True
4. rotate_angle=450
5. dlib_file="src/weight/shape_predictor_68_face_landmarks.dat"
