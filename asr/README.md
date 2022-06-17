# ASR module

ASR Module ใช้สำหรับแปลงสัญญาณเสียงเป็นข้อมูลประเภท Text โดยที่ใช้ Model ASR ที่ถูกแปลงเป็น ONNX model

## Model conversion
การแปลง Model ASR จาก Huggingface model ทางผู้จัดทำได้ [Colab](https://github.com/Intraraksa/restructure_meta_human/blob/master/asr/project_asr2onnx.ipynb) สำหรับแปลง Model เป็น ONNX เอาไว้รวมถึงวิธีการ Inference ONNX model เอาไว้ และการ inference ได้ถูกทำเป็น Module class object เอาไว้เพื่อให้ใช้งานได้โดยง่าย
