import torch
import json
import cv2
import numpy as np
from torchvision.transforms import transforms

from main import load_model
from utils.ImageProcess import std_coordinate
from utils.ImageProcess import ImageProcess
from models import KeyPointLearner
from conf import *
from utils.Visualizer import Visualizer


def split_frame_json(json_file):
    res = []
    for elem in json_file:
        image_id = elem['image_id'][:elem['image_id'].find('.')]
        frame_sub = eval(image_id)
        if frame_sub >= len(res):
            res.append([elem])
        else:
            res[frame_sub].append(elem)
    return res


def check_frame(sub, data):
    for elem in data:
        image_id = elem[0]['image_id'][:elem[0]['image_id'].find('.')]
        frame_sub = eval(image_id)
        if sub == frame_sub:
            return True
    return False


def paint(frame, frame_sub, frame_data, learner, scan_cnt, keypoints_num):
    if not check_frame(frame_sub, frame_data):
        return frame
    person_list = frame_data[frame_sub]
    cnt = 0
    for element in person_list:
        if element['score'] > 1.:
            np_keypoints = np.array(element['keypoints'])
            np_keypoints = std_coordinate(1, 1, element['box'], np_keypoints, 26)[:keypoints_num, :]
            keypoints_m = ImageProcess.__get_matrix__(np_keypoints, keypoints_num)
            keypoints = transforms.ToTensor()(np_keypoints)
            keypoints_m = transforms.ToTensor()(keypoints_m)

            keypoints = torch.unsqueeze(keypoints, dim=0).to(torch.float)
            keypoints_m = torch.unsqueeze(keypoints_m, dim=0).to(torch.float)

            pred = learner(keypoints, keypoints_m).argmax(dim=1)
            for k, v in NAME_MAP.items():
                if v == pred.item():
                    frame = Visualizer.show_anchor(frame, element)
                    # frame = Visualizer.show_line(frame, element)
                    clr = (0, 0, 255)
                    if k == 'stand':
                        clr = (255, 0, 0)
                    elif k == 'handsup':
                        clr = (0, 255, 0)
                    frame = Visualizer.show_label(frame, element, k, clr)
            cnt += 1
            if cnt == scan_cnt:
                return frame
    return frame


if __name__ == '__main__':
    with open('../test/resource/video/alphapose-results.json', 'r') as fp:
        json_file = json.load(fp)

    frame_data = split_frame_json(json_file)
    learner = KeyPointLearner()
    load_model('../test/resource/model.pkl', learner)

    cap = cv2.VideoCapture("../test/resource/video/demo_stand_sit.avi")  # 读取视频文件
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('../test/resource/video/output.avi', fourcc, 30, (frame_w, frame_h))
    frame_cnt = 0
    while True:
        ret, frame = cap.read()
        if ret:
            frame = paint(frame, frame_cnt, frame_data, learner, -1, keypoints_num=26)
            frame_cnt += 1
            out.write(frame)
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()