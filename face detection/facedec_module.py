## This file is module for face_det_video.py
import numpy as np
import math
import cv2
import dlib
import os, shutil, subprocess
import time
import base64
from PIL import Image
from io import BytesIO
import pickle
import socketio

from keras.models import load_model
from fer import FER

src = os.getcwd()
sio = socketio.Client()

blank_head_x =[]#[0]*5
blank_head_y =[]#[0]*5
blank_head_z =[]#[0]*5
param_check = False
# seq_emo = [[0] * 7] * 5
time_step_data = 15


class Face_dec():
    detector_emo = FER(mtcnn=True)
    def __init__(self,weight_model="src/weight/model_15frame_adddata.h5",pickle_file="src/rpy_tee.pickle",mtcnn=True,rotate_angle=450,dlib_file="src/weight/shape_predictor_68_face_landmarks.dat"):
        self.test_load_model = load_model(weight_model) #"src/weight/model_15frame_adddata.h5"
        self.shape_predictor = dlib.shape_predictor(dlib_file)
        self.cnn_face_detector = dlib.get_frontal_face_detector()
        self.rotage_head_frame = rotate_angle #450
        self.face_img = np.zeros((500, 500, 3))
        self.face4unity = False
        self.facereg_new = False
        self.facelock = [True]
        self.facecd = [0.00]
        self.seq_emo = [[0] * 7] * 5 
        with open(pickle_file, 'rb') as handle: # "src/rpy_tee.pickle"
            self.rotage_head = pickle.load(handle)

        # encode image to string base64
    def string_encode(self,fimg):
        fimg_rgb = cv2.cvtColor(fimg, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(fimg_rgb.astype(np.uint8))
        im_file = BytesIO()
        img.save(im_file, format="JPEG")
        # im_bytes: image in binary format.
        im_bytes = im_file.getvalue()
        face_encode = base64.b64encode(im_bytes)
        # print(face_encode)
        print(type(face_encode))
        return face_encode


    # convert rect object(dlib) to tuple
    def rect_to_bb(self,rect):
        # take a bounding predicted by dlib and convert it
        # to the format (x, y, w, h) as we would normally do
        # with OpenCV
        x = rect.left()
        y = rect.top()
        w = rect.right() - x
        h = rect.bottom() - y
        # return a tuple of (x, y, w, h)
        return (x, y, w, h)


    # convert shape object(dlib) to facial landmark numpy
    def shape_to_np(self,shape, dtype="int"):
        # initialize the list of (x, y)-coordinates
        coords = np.zeros((68, 2), dtype=dtype)
        # loop over the 68 facial landmarks and convert them
        # to a 2-tuple of (x, y)-coordinates
        for i in range(0, 68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
        # return the list of (x, y)-coordinates
        return coords


    # compute angle degree
    def getAngleDegree(self,p1x, p1y, p2x, p2y):
        angleDeg = math.fabs(math.atan2(p2y - p2y, p2x - p1x) * 180 / math.pi);
        return angleDeg


    # check straight face
    def isStraightFace(self,landmarkP):
        straightFace_bool = False
        # find angle degree from landmark point
        # l = left, m = mid, r = right
        dis_lr = self.getAngleDegree(landmarkP[0][0], landmarkP[0][1], landmarkP[16][0], landmarkP[16][1])
        dis_lm = self.getAngleDegree(landmarkP[0][0], landmarkP[0][1], landmarkP[27][0], landmarkP[27][1])
        dis_mr = self.getAngleDegree(landmarkP[27][0], landmarkP[27][1], landmarkP[16][0], landmarkP[16][1])
        dis_mid = self.getAngleDegree(landmarkP[27][0], landmarkP[27][1], landmarkP[8][0], landmarkP[8][1])

        # find distance
        distL = math.fabs(landmarkP[27][0] - landmarkP[0][0])
        distR = math.fabs(landmarkP[27][0] - landmarkP[16][0])
        maxX = max(distL, distR)
        distX = math.fabs(distL - distR)
        print(distL)
        print(distR)
        print(maxX)
        print(distX)
        print(dis_mid, 'dis_mid')
        if (dis_lr <= 7 and dis_lm <= 7 and dis_mr <= 7 and distX <= maxX * 0.3):
            straightFace_bool = True

        return straightFace_bool


    # set path
    # path_root = os.getcwd()
    # path_src = os.path.join(path_root, "src")
    # path_weight = os.path.join(path_src, "weight")

    # load face and facial landmark detection model

    # change state for send face image to unity
    def chg_face_lock_stat(self,face_lock_stat):
        self.facelock[0] = face_lock_stat
        self.facecd[0] = time.time()


    # set value x to min <= x <= max
    def clamp(self,n, minn, maxn):
        return max(min(maxn, n), minn)


    def detectemotion(self,img, codinates):
        res = self.detector_emo.detect_emotions(img, codinates)
        return res

    def change_param_check(self,param_check_):
        param_check = param_check_
        return param_check

    def send_rpy(self,blank_head_x=blank_head_x,blank_head_y=blank_head_y,blank_head_z=blank_head_z): # ลบ rotage_head_frame
        blank_head_x.append(max(min(self.rotage_head[self.rotage_head_frame]['angle'][0],2),-2))
        blank_head_y.append(self.rotage_head[self.rotage_head_frame]['angle'][1]-4)
        blank_head_z.append(max(min(self.rotage_head[self.rotage_head_frame]['angle'][2],3),-3))
        self.rotage_head_frame = self.rotage_head_frame + 5
        print(blank_head_x,self.rotage_head_frame)
        if len(blank_head_x) > 5 :
            param_x = sum(blank_head_x)/len(blank_head_x) #* 3
            param_y = sum(blank_head_y)/len(blank_head_y) * 3
            param_z = sum(blank_head_z)/len(blank_head_z) #* 3
            # sio.emit("send_rpy_estimation","x:{}|y:{}|z:{}".format(param_x,param_y,param_z))
            # print("x:{}|y:{}|z:{}".format(sum(blank_head_x)/len(blank_head_x),sum(blank_head_y)/len(blank_head_y),sum(blank_head_z)/len(blank_head_z)))
            blank_head_x = blank_head_x[:3]
            blank_head_y = blank_head_y[:3]
            blank_head_z = blank_head_z[:3]
        return self.rotage_head_frame

    def playVideo(self,video_file=0): #
        cap = cv2.VideoCapture(video_file)
        while (cap.isOpened()):
            start_time = time.time()

            # Read Image
            ret, img = cap.read()
            if ret != True:
                print('read frame failed')
                # continue
                break
            size = img.shape

            # if image size is large -> resize image for less compute cost
            if size[0] > 900:
                h = size[0] / 3
                w = size[1] / 3
                img = cv2.resize(img, (int(w), int(h)), interpolation=cv2.INTER_CUBIC)
                size = img.shape

            # send image if facelock[0] is false
            if (not self.facelock[0]):
                # send to "recv_face_img" in Unity
                # sio.emit("face_img", self.string_encode(img))
                pass
            cv2.imshow('preview',img)

            # face detection
            dets = self.cnn_face_detector(img, 1)
            # find face image with maximum bounding box size and assign value w h x y
            if len(dets) > 0:
                bb_size = []
                max_bb_size = 0
                max_bb_size_idx = 0
                face_w = size[1]
                face_h = size[0]
                face_x = size[1] / 2
                face_y = size[0] / 2
                for idx_bb in range(len(dets)):
                    face = dets[idx_bb]
                    (x, y, w, h) = self.rect_to_bb(face)
                    if w * h > max_bb_size:
                        max_bb_size = w * h 
                        max_bb_size_idx = idx_bb
                        face_w = w
                        face_h = h
                        face_x = x
                        face_y = y

                # get face max size and find facial landmark
                face = dets[max_bb_size_idx]
                shape = self.shape_predictor(img, face)
                landmark = self.shape_to_np(shape)

                # set value min <= x <= max
                face_w = self.clamp(face_w, 0, img.shape[1])
                face_x = self.clamp(face_x, 0, img.shape[1])
                face_h = self.clamp(face_h, 0, img.shape[0])
                face_y = self.clamp(face_y, 0, img.shape[0])

                # send center of face detection position to unity for control 3D model look at sphere
                face_pos_x = face_x + face_w / 2
                face_pos_y = face_y + face_h / 2
                face_pos_x = (face_pos_x - 320) / 640
                face_pos_y = (face_pos_y - 320) / 640

                # sio.emit("send_face_pos", "start:" + str(face_pos_x) + ":" + str(face_pos_y) + ":end")

                self.face_img = img[face_y: face_y + face_h, face_x: face_x + face_w] 
                face_codinate = [[face_x, face_y, face_w, face_h]]
                if param_check:
                    print(param_check,'param_check')
                    rotage_head_frame = self.send_rpy(rotage_head_frame)

                emotion_res = self.detectemotion(img, face_codinate)
                data_emotion = list(emotion_res[0]['emotions'].values())
                list_emotion = list(emotion_res[0]['emotions'].keys())
                self.seq_emo.append(data_emotion)

                if len(self.seq_emo) > time_step_data - 1:
                    seq_emo_ = np.asarray(self.seq_emo)
                    seq_emo_ = np.expand_dims(seq_emo_, axis=0)
                    res_test = self.test_load_model.predict(seq_emo_)
                    res_test = list(np.clip(res_test, 0, 1))
                    self.seq_emo = self.seq_emo[2:]  # edit
                    test_result_pred = dict(zip(list_emotion, res_test[0][-1]))
                    # sio.emit("send_pose_estimation",
                    #         "More_Angry:{}|Fear:{}|Happy:{}|More_Sad:{}|Surprise:{}".format(res_test[0][-1][0],
                    #                                                                         res_test[0][-1][2],
                    #                                                                         res_test[0][-1][3] * 0.6,
                    #                                                                         res_test[0][-1][4],
                    #                                                                         res_test[0][-1][5]))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

            # if face not lock it will send straight face image to unity
                # print(facelock[0])
                if (not self.facelock[0]):
                    self.face4unity = True
                    sio.emit("face_img", self.string_encode(img))

                    # countdown 3s for send straight face image
                    if ((time.time() - self.facecd[0]) < 3.0):
                        time.sleep(0.1)
                        continue



                    # check if is straight face image
                    faceSF = self.isStraightFace(landmark)
                    print(faceSF)

                    # if it send to unity already it will be stop send next image
                    if faceSF and self.face4unity:

                        self.facereg_new = True;
                        if (self.facereg_new):
                            self.facelock[0] = True
                            self.face4unity = False
                            self.facereg_new = False
                            self.face_img = img[face_y: face_y + face_h, face_x: face_x + face_w]
                            # send to "recv_face_img" in Unity
                            sio.emit("face_img", self.string_encode(self.face_img))
                            # send to "recv_face_conf" in Unity
                            sio.emit("open_face_conf", "open");
                            # clear face image to null
                            self.face_img = np.zeros((500, 500, 3))
                            print("SF")

                # if send image time sleep for delay
                time.sleep(0.1)
            else:
                # if not send image time sleep for delay but longer than send image time
                time.sleep(0.2)
                continue


