#! /usr/bin/env python
# coding=utf-8
# ================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   Editor      : VIM
#   File name   : config.py
#   Author      : YunYang1994
#   Created date: 2019-02-28 13:06:54
#   Description :
#
# ================================================================

from easydict import EasyDict as edict

import config as config

prefix = config.prefix
__C = edict()
# Consumers can get config by: from config import cfg

cfg = __C

# YOLO options
__C.YOLO = edict()

# Set the class name
# __C.SCENE.CLASSES               = "./data/classes/ui.names" 
__C.YOLO.CLASSES = prefix + "/data/classes/ui3class.names"  # 实列的类名，相当于之前的CLASSNUM.json,80类
__C.YOLO.ANCHORS = prefix + "/data/anchors/basline_anchors.txt"
__C.YOLO.MOVING_AVE_DECAY = 0.9995
__C.YOLO.STRIDES = [8, 16, 32]
__C.YOLO.ANCHOR_PER_SCALE = 3
__C.YOLO.IOU_LOSS_THRESH = 0.5
__C.YOLO.UPSAMPLE_METHOD = "resize"  # 上采样采用resize是否需要改
__C.YOLO.ORIGINAL_WEIGHT = prefix + "/checkpoint/yolov3_coco.ckpt"
__C.YOLO.DEMO_WEIGHT = prefix + "/checkpoint/yolov3_coco_demo.ckpt"
__C.YOLO.FOCALLOSS_ALPHA = prefix + "/data/class_wight/alpha2Li.json"

# Set the scenarios class name
# __C.CustomizedModel.CLASSES     = "./data/classes/XXX"#added by tendoyo, we need to specify what scenarios we need to handle
# __C.CustomizedModel.YOLO.TRAINED_WEIGHT = "./checkpoint/XXXX"  # added by tendoyo, here is the trained weight of Yolo

# Train options
__C.TRAIN = edict()

__C.TRAIN.ANNOT_PATH = prefix + "/data/dataset/25filter_train.txt"  # 里面包含图片的地址和
__C.TRAIN.BATCH_SIZE = 4  # 6
# TODO by zhangz 修改尺寸
# __C.TRAIN.INPUT_SIZE            = 1088 // 2
__C.TRAIN.INPUT_SIZE = [320, 352, 384, 416, 448, 480, 512, 544, 576, 608]
__C.TRAIN.DATA_AUG = True  # 是否进行图片增强
__C.TRAIN.LEARN_RATE_INIT = 1e-4
__C.TRAIN.LEARN_RATE_END = 1e-6
__C.TRAIN.WARMUP_EPOCHS = 2
__C.TRAIN.FISRT_STAGE_EPOCHS = 20
# __C.TRAIN.FISRT_STAGE_EPOCHS    = 0
__C.TRAIN.SECOND_STAGE_EPOCHS = 50  # 30
__C.TRAIN.INITIAL_WEIGHT = prefix + "/checkpoint/yolov3_coco_demo.ckpt"  # TODO 接着训练改这里
# __C.TRAIN.INITIAL_WEIGHT        = "./zhangz_checkpoint/yolov3_15_loss=115.2365.ckpt-5" 


# TEST options
__C.TEST = edict()

__C.TEST.ANNOT_PATH = prefix + "/Pretrain/temp_test_test.txt"
__C.TEST.BATCH_SIZE = 1
__C.TEST.INPUT_SIZE = 512
__C.TEST.DATA_AUG = False
__C.TEST.WRITE_IMAGE = True
__C.TEST.WRITE_IMAGE_PATH = prefix + "/data/evaluate_classifier/"
__C.TEST.WRITE_IMAGE_SHOW_LABEL = True
__C.TEST.WEIGHT_FILE = prefix + "/checkpoint/re17wan_yolov3_2_loss=31.1663.ckpt-46"
__C.TEST.SHOW_LABEL = True
__C.TEST.SCORE_THRESHOLD = 0.3
__C.TEST.IOU_THRESHOLD = 0.45
