#! /usr/bin/env python
# coding=utf-8
#================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   Editor      : VIM
#   File name   : dataset.py
#   Author      : YunYang1994
#   Created date: 2019-03-15 18:05:03
#   Description :
#
#================================================================

import os
import cv2
import random
import numpy as np
import tensorflow as tf
from dynamicExerciser.picLabel.core import utils as utils
from dynamicExerciser.picLabel.core import config as cfg

TRAIN_ANNOT_PATH = r'/home/yh/gitCode/tensorflow-picLabel/data/dataset/cutadd_class25train.txt'
# TRAIN_ANNOT_PATH = r'/home/yh/gitCode/tensorflow-picLabel/data/dataset/class7train.txt'
TRAIN_BATCH_SIZE = 10
TRAIN_DATA_AUG = True

TEST_ANNOT_PATH = r'/home/yh/gitCode/tensorflow-picLabel/data/dataset/cutadd_class25val.txt'
# TEST_ANNOT_PATH = r'/home/yh/gitCode/tensorflow-picLabel/data/dataset/class7test.txt'
TEST_BATCH_SIZE = 10
TEST_DATA_AUG = False

class Dataset(object):
    """implement Dataset here"""
    def __init__(self, dataset_type):
        self.annot_path  = TRAIN_ANNOT_PATH if dataset_type == 'train' else TEST_ANNOT_PATH
        # self.input_sizes = cfg.TRAIN.INPUT_SIZE if dataset_type == 'train' else cfg.TEST.INPUT_SIZE
        self.batch_size  = TRAIN_BATCH_SIZE if dataset_type == 'train' else TEST_BATCH_SIZE
        self.data_aug    = TRAIN_DATA_AUG if dataset_type == 'train' else TEST_DATA_AUG

        self.train_input_size = 512
        self.strides = np.array(cfg.YOLO.STRIDES)
        self.classes = utils.read_class_names(cfg.YOLO.CLASSES)
        self.num_classes = len(self.classes)
        self.anchors = np.array(utils.get_anchors(cfg.YOLO.ANCHORS))
        self.anchor_per_scale = cfg.YOLO.ANCHOR_PER_SCALE
        self.max_bbox_per_scale = 150

        self.annotations = self.load_annotations(dataset_type)
        self.num_samples = len(self.annotations)
        self.num_batchs = int(np.ceil(self.num_samples / self.batch_size))
        self.batch_count = 0
        # TODO
        self.groud_truth = []


    def load_annotations(self, dataset_type):
        with open(self.annot_path, 'r') as f:
            txt = f.readlines()
            annotations = [line.strip() for line in txt if len(line.strip().split('$&')[1:]) != 0]
        np.random.shuffle(annotations)
        # TODO  只读100张
        # annotations = annotations[:100]
        return annotations

    def __iter__(self):
        return self

    def __next__(self):
 
        with tf.device('/cpu:0'):
            # # TODO by zhangz 修改尺寸
            # self.train_input_size_h = 512
            # self.train_input_size_w = 512
            # self.train_input_size = random.choice(self.train_input_sizes)
            self.train_input_size = 512
            self.train_output_sizes = self.train_input_size // self.strides
            # self.train_output_sizes_h = self.train_input_size_h // self.strides  #输出的三种feature map的长宽
            # self.train_output_sizes_w = self.train_input_size_w // self.strides

            batch_image = np.zeros((self.batch_size, self.train_input_size, self.train_input_size, 3))

            num = 0
            if self.batch_count < self.num_batchs:
                self.groud_truth = []
                class_id = []
                while num < self.batch_size:
                    index = self.batch_count * self.batch_size + num
                    if index >= self.num_samples: index -= self.num_samples
                    annotation = self.annotations[index]
                    # TODO
                    self.groud_truth.append(annotation)
                    image, label= self.parse_annotation(annotation)
                    class_id.append(label)

                    batch_image[num, :, :, :] = image
                    num += 1
                self.batch_count += 1
                return batch_image, class_id
            else:
                self.batch_count = 0
                np.random.shuffle(self.annotations)
                raise StopIteration

    def random_horizontal_flip(self, image, bboxes):

        if False:
        # if True:
            _, w, _ = image.shape
            image = image[:, ::-1, :]
            bboxes[:, [0,2]] = w - bboxes[:, [2,0]]

        return image, bboxes

    def random_crop(self, image, bboxes): 

        if random.random() < 0.5:
        # if True:
            h, w, _ = image.shape
            max_bbox = np.concatenate([np.min(bboxes[:, 0:2], axis=0), np.max(bboxes[:, 2:4], axis=0)], axis=-1)

            max_l_trans = max_bbox[0]
            max_u_trans = max_bbox[1]
            max_r_trans = w - max_bbox[2]
            max_d_trans = h - max_bbox[3]

            crop_xmin = max(0, int(max_bbox[0] - random.uniform(0, max_l_trans)))
            crop_ymin = max(0, int(max_bbox[1] - random.uniform(0, max_u_trans)))
            crop_xmax = max(w, int(max_bbox[2] + random.uniform(0, max_r_trans)))
            crop_ymax = max(h, int(max_bbox[3] + random.uniform(0, max_d_trans)))

            image = image[crop_ymin : crop_ymax, crop_xmin : crop_xmax]

            bboxes[:, [0, 2]] = bboxes[:, [0, 2]] - crop_xmin
            bboxes[:, [1, 3]] = bboxes[:, [1, 3]] - crop_ymin

        return image, bboxes

    def random_translate(self, image, bboxes):

        if random.random() < 0.5:
        # if True:
            h, w, _ = image.shape
            max_bbox = np.concatenate([np.min(bboxes[:, 0:2], axis=0), np.max(bboxes[:, 2:4], axis=0)], axis=-1)

            max_l_trans = max_bbox[0]
            max_u_trans = max_bbox[1]
            max_r_trans = w - max_bbox[2]
            max_d_trans = h - max_bbox[3]

            tx = random.uniform(-(max_l_trans - 1), (max_r_trans - 1))
            ty = random.uniform(-(max_u_trans - 1), (max_d_trans - 1))

            M = np.array([[1, 0, tx], [0, 1, ty]])
            image = cv2.warpAffine(image, M, (w, h))

            bboxes[:, [0, 2]] = bboxes[:, [0, 2]] + tx
            bboxes[:, [1, 3]] = bboxes[:, [1, 3]] + ty

        return image, bboxes

    def parse_annotation(self, annotation):

        line = annotation.split('$&')
        image_path = line[0]
        # print("[DOING] " + image_path)
        if not os.path.exists(image_path):
            raise KeyError("%s does not exist ... " %image_path)

        label = line[1]

        # TODO by zhangz resize图片大小
        img = cv2.imread(image_path)
        # img = cv2.resize(img, (1080, 1794), interpolation=cv2.INTER_CUBIC)
        image = np.array(img)
        image = cv2.resize(image, (1080, 1731))
        # image = cv2.imread(image_path)
        # size = (512, 512)
        # image = cv2.resize(image, size)
        # image = np.array(image)

        # if self.data_aug:
        #     image, bboxes = self.random_horizontal_flip(np.copy(image), np.copy(bboxes))  #平移
        #     image, bboxes = self.random_crop(np.copy(image), np.copy(bboxes)) 
        #     image, bboxes = self.random_translate(np.copy(image), np.copy(bboxes))   #相当于三种预处理
        # TODO 
        image = utils.image_preporcess(np.copy(image), [self.train_input_size, self.train_input_size])
        
        return image, label

    def __len__(self):
        return self.num_batchs

 


