#! /usr/bin/env python
# coding=utf-8
#================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Editor      : Visual Code
#   File name   : customizedmodel.py
#   Author      : tendoyo & Zhangz
#   Created date: 2020-12-30 15:33:03
#   Description :
#
#================================================================
import numpy as np
import tensorflow as tf
from dynamicExerciser.picLabel.core import utils as utils
# import core.common as common
# import core.backbone as backbone
from dynamicExerciser.picLabel.core.yolov3 import YOLOV3
from dynamicExerciser.picLabel.core.vgg16_testonecls import VGG16
from dynamicExerciser.picLabel.core.config import cfg


class CustomizedModel(object):
    """Implement tensoflow custmoized model to classify app scenarios here"""
    def __init__(self, input_data, input_labels, trainable):
        # 预训练参数
        self.yolo_classes     = utils.read_class_names(cfg.YOLO.CLASSES)  #类名
        self.yolo_num_class   = len(self.yolo_classes)  #类数量
        self.in_channel       = 3 * (self.yolo_num_class + 5)

        self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video", "TakeOut", "shop_list", "APPshop_list"]
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video"]
        self.num_class = len(self.classes)

        try:
            self.combineembedding = self.__build_network(input_data, input_labels, trainable)
        except:
            raise NotImplementedError("Can not build up our customized network!")

    def __build_network(self, input_data, input_labels, trainable): 
        yolo             = YOLOV3(input_data, trainable) #初始化yolo，作为我们的前缀网络结构
        conv_lbbox       = yolo.conv_lbbox  #y1 [13, 13, ?]
        conv_mbbox       = yolo.conv_mbbox  #y2 [26, 26, ?]
        conv_sbbox       = yolo.conv_sbbox  #y3用于分类时应该是使用的这个输出 [52, 52, ?]

        # sbbox_output = VGG16(conv_sbbox, input_labels, 'vgg_sbbox').model
        lbbox_output = VGG16(conv_lbbox, conv_mbbox, conv_sbbox, input_labels, 'vgg_lbbox').model
        # mbbox_output = VGG16(conv_mbbox, input_labels, 'vgg_mbbox').model

        all_softmax_output = lbbox_output['output']
        all_cost = lbbox_output['cost']

        # with tf.control_dependencies([lbbox_output['optimize'], mbbox_output['optimize'], sbbox_output['optimize']]):
            # all_optimize = tf.no_op()

        prediction_labels = tf.argmax(all_softmax_output, axis=1, name="output")
        read_labels = tf.argmax(input_labels, axis=1)

        correct_prediction = tf.equal(prediction_labels, read_labels)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.int32))

        correct_times_in_batch = tf.reduce_sum(tf.cast(correct_prediction, tf.int32))

        return dict(
            x=input_data,
            y=input_labels,
            # optimize=all_optimize,
            loptimize=lbbox_output['optimize'],
            # lbbox_out
            l_out=dict(
                cost=lbbox_output['cost'],
                correct_prediction=lbbox_output['correct_prediction'],
                correct_times_in_batch=lbbox_output['correct_times_in_batch'],
                prediction_labels=lbbox_output['prediction_labels']
            )
        )

    def fc_layer(self, inputtf, input_size, output_size, name):

        if input_size is None:
            input_size = int(np.prod(inputtf.get_shape()[1:]))
            inputtf = tf.reshape(inputtf, [-1, input_size])

        kernel = tf.Variable(tf.truncated_normal([input_size, output_size], dtype=tf.float32, stddev=0.1))
        biases = tf.Variable(tf.constant(0.1, dtype=tf.float32, shape=[output_size]))
        
        output = tf.nn.relu(tf.matmul(inputtf, kernel) + biases, name=name)

        return output

