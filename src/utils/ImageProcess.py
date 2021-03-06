import json
from pathlib import Path

import cv2
import numpy as np


def find_person(img_data):
    index = 0
    max_area = 0
    for i, person in enumerate(img_data):
        area = person['box'][2] * person['box'][3]
        if area > max_area and person['score'] > 1.:
            max_area = area
            index = i
    # print(index, img_data)
    if len(img_data) == 0:
        return None
    return img_data[index]


def split_person_dict(img_name, dict_all):
    # print(img_name)
    return find_person([meta for meta in dict_all if meta['image_id'] == img_name])


def std_coordinate(std_h, std_w, box, keypoints, kp_total):
    x, y, h, w = box
    # np_points = np.array(keypoints).reshape((26, 3))
    np_points = np.array(keypoints).reshape((len(keypoints) // 3, 3))
    np_points[:, 0] = (np_points[:, 0] - x) / h * std_h
    np_points[:, 1] = (np_points[:, 1] - y) / w * std_w
    # np_points[np_points < 0] = 0
    return np_points


class ImageProcess:
    def __init__(self, in_path):
        self.in_path = Path(in_path)
        # self.out_path = Path(out_path)
        with open(self.in_path / 'alphapose-results.json', 'r') as fp:
            self.json_file = json.load(fp)

    def __get_keypoints__(self, img_path, keypoints_num, std_h, std_w):
        person_dict = split_person_dict(img_path.name, self.json_file)
        if person_dict is None:
            return None
        # if len(person_dict['keypoints']) == 408:
        #     print(person_dict['image_id'])
        keypoints_xyp = std_coordinate(std_h, std_w, person_dict['box'], person_dict['keypoints'], 26)
        return keypoints_xyp[:keypoints_num]

    @staticmethod
    def __get_matrix__(keypoints, num):
        l = np.array([keypoints[19][:2]])
        # keypoints = np.array(keypoints)
        # keypoints[:, 0] = keypoints[:, 0] * keypoints[:, 2]
        # keypoints[:, 1] = keypoints[:, 1] * keypoints[:, 2]
        result = np.repeat(l, num, -2) - keypoints[:, :2]
        # result = result * np.repeat(np.array([keypoints[:, 2]]), 2, 0).T

        l1 = np.array([keypoints[0][:2]])
        result1 = np.repeat(l1, num, -2) - keypoints[:, :2]

        result = result @ result1.T

        # for i, line in enumerate(keypoints):
        #     l = np.array([line[:2]])
        #     temp = (np.repeat(l, num, -2) - keypoints[:, :2])
        #     temp[i] = (1e-5, 1e-5)
        #     # temp_2 = np.sqrt(np.sum(temp ** 2, axis=1))
        #     # temp_2 = np.repeat(temp_2, 2, 0)
        #     # temp = temp / np.reshape(temp_2, temp.shape)
        #
        #     # temp = np.sqrt(np.sum(temp, axis=1))
        #     # temp = temp / keypoints[:, 2]
        #     # print(temp.size())
        #     # temp = (temp - np.mean(temp)) / np.std(temp)
        #     result[i] = temp
        return result

    def get_keypoints(self, keypoints_num, std_h, std_w):
        for img_path in self.in_path.rglob('*.jpg'):
            keypoints = self.__get_keypoints__(img_path, keypoints_num, std_h, std_w)
            if keypoints is None:
                continue
            yield img_path.stem, keypoints

    def get_data(self, keypoints_num, std_h, std_w):
        for img_name, keypoints in self.get_keypoints(keypoints_num, std_h, std_w):
            keypoints_pm = np.array([keypoints[:, 2]]).T
            # keypoints_pm = np.repeat(keypoints_pm, repeats=26, axis=0)
            # keypoints_pm = np.matmul(np.transpose(keypoints_pm), keypoints_pm)
            # keypoints_pm = keypoints_pm / np.sum(keypoints_pm, axis=1)
            yield img_name, keypoints_pm, ImageProcess.__get_matrix__(keypoints, keypoints_num)


if __name__ == '__main__':
    ip = ImageProcess(in_path='../../test/resource/res')
    for name, m in ip.get_data(26, 5, 5):
        print(name, m)
        input()
