#! /usr/bin/env python
# coding=utf-8
# ================================================================
#   Copyright (C) 2020 * Ltd. All rights reserved.
#
#   Editor      : Visual Code
#   File name   : customizedmodel.py
#   Author      : tendoyo & Zhangz
#   Created date: 2020-12-30 15:33:03
#   Description :
#
# ================================================================
import tensorflow as tf
from dynamicExerciser.picLabel.core import common as common, utils as utils
# import core.backbone as backbone
# from core.picLabel import YOLOV3
from dynamicExerciser.picLabel.core.config import cfg


class VGG16(object):
    """Implement tensoflow custmoized model to classify app scenarios here"""

    def __init__(self, input_data, input_labels, name):
        # 预训练参数
        self.yolo_classes = utils.read_class_names(cfg.YOLO.CLASSES)  # 类名
        self.yolo_num_class = len(self.yolo_classes)  # 类数量
        self.in_channel = 3 * (self.yolo_num_class + 5) + 52

        self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video", "TakeOut", "shop_list",
                        "APPshop_list"]
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video"]
        self.num_class = len(self.classes)

        try:
            self.model = self.__build_network(input_data, input_labels, name)
        except:
            raise NotImplementedError("Can not build up our customized network!")

    def __build_network(self, input_data, input_labels, name):

        with tf.variable_scope(name):
            # #Block 1
            # in_channel = self.in_channel
            # out_channel = self.in_channel
            # conv1_1 = common.convolutional(input_data=input_data, 
            #                                filters_shape=(3, 3, in_channel, out_channel), 
            #                                trainable=True, name='conv1_1')
            # pool1 = tf.nn.max_pool(conv1_1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], 
            #                        padding='SAME', name='pool1')

            # #Block2
            # in_channel = out_channel
            # out_channel = in_channel * 2
            # conv2_1 = common.convolutional(input_data=pool1, 
            #                                filters_shape=(3, 3, in_channel, out_channel), 
            #                                trainable=True, name='conv2_1')
            # conv2_2 = common.convolutional(input_data=conv2_1, 
            #                                filters_shape=(3, 3, out_channel, out_channel), 
            #                                trainable=True, name='conv2_2')
            # pool2 = tf.nn.max_pool(conv2_2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], 
            #                        padding='SAME', name='pool2')

            # 由于输入向量大小相对较小, lbox(16*16) 做一次池化, mbox 两次, sbox 三次
            # Block3 
            in_channel = self.in_channel
            out_channel = in_channel
            conv3_1 = common.convolutional(input_data=input_data,
                                           filters_shape=(3, 3, in_channel, out_channel),
                                           trainable=True, name='conv3_1')
            conv3_2 = common.convolutional(input_data=conv3_1,
                                           filters_shape=(3, 3, out_channel, out_channel),
                                           trainable=True, name='conv3_2')
            fin = common.convolutional(input_data=conv3_2,
                                       filters_shape=(3, 3, out_channel, out_channel),
                                       trainable=True, name='conv3_3')
            # pool = tf.nn.max_pool(conv3_3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], 
            #                        padding='SAME', name='pool3')

            # #Block4
            # if name in ['vgg_mbbox', 'vgg_sbbox']:
            #     in_channel = out_channel
            #     out_channel = in_channel * 2
            #     conv4_1 = common.convolutional(input_data=pool, 
            #                                 filters_shape=(3, 3, in_channel, out_channel), 
            #                                 trainable=True, name='conv4_1')
            #     conv4_2 = common.convolutional(input_data=conv4_1, 
            #                                 filters_shape=(3, 3, out_channel, out_channel), 
            #                                 trainable=True, name='conv4_2')
            #     conv4_3 = common.convolutional(input_data=conv4_2, 
            #                                 filters_shape=(3, 3, out_channel, out_channel), 
            #                                 trainable=True, name='conv4_3')
            #     pool = tf.nn.max_pool(conv4_3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], 
            #                         padding='SAME', name='pool4')

            # #Block5
            if name in ['vgg_sbbox', 'vgg_mbbox']:
                #     in_channel = out_channel
                #     out_channel = in_channel * 2
                #     conv5_1 = common.convolutional(input_data=pool,
                #                                 filters_shape=(3, 3, in_channel, out_channel),
                #                                 trainable=True, name='conv5_1')
                #     conv5_2 = common.convolutional(input_data=conv5_1,
                #                                 filters_shape=(3, 3, out_channel, out_channel),
                #                                 trainable=True, name='conv5_2')
                #     conv5_3 = common.convolutional(input_data=conv5_2,
                #                                 filters_shape=(3, 3, out_channel, out_channel),
                #                                 trainable=True, name='conv5_3')
                fin = tf.nn.max_pool(fin, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                                     padding='SAME', name='pool5')
            if name in ['vgg_sbbox']:
                #     in_channel = out_channel
                #     out_channel = in_channel * 2
                #     conv5_1 = common.convolutional(input_data=pool,
                #                                 filters_shape=(3, 3, in_channel, out_channel),
                #                                 trainable=True, name='conv5_1')
                #     conv5_2 = common.convolutional(input_data=conv5_1,
                #                                 filters_shape=(3, 3, out_channel, out_channel),
                #                                 trainable=True, name='conv5_2')
                #     conv5_3 = common.convolutional(input_data=conv5_2,
                #                                 filters_shape=(3, 3, out_channel, out_channel),
                #                                 trainable=True, name='conv5_3')
                fin = tf.nn.max_pool(fin, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                                     padding='SAME', name='pool5')

            # fc
            # flatten = tf.keras.layers.Flatten()(pool5)
            flatten = tf.keras.layers.Flatten()(fin)
            output = tf.keras.layers.Dense(units=4096, use_bias=True, name='fc1', activation='relu')(flatten)
            output = tf.keras.layers.Dense(units=4096, use_bias=True, name='fc2', activation='relu')(output)
            output = tf.keras.layers.Dense(units=self.num_class, use_bias=True, name='fc3', activation=None)(output)

            finaloutput = tf.nn.softmax(output, name="softmax")

            cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=output, labels=input_labels))

            all_vars = tf.global_variables()
            c_vars = [v for v in all_vars if v.name.split('/')[0].startswith(name)]
            # print(c_vars)
            # IPython.embed()

            # moving_ave = tf.train.ExponentialMovingAverage(0.9995).apply(c_vars)

            # with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
            #     with tf.control_dependencies([moving_ave]):
            #         optimize = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(cost, var_list=c_vars)
            # optimize = tf.train.AdadeltaOptimizer(learning_rate=1e-5, name="conv_all_op").minimize(cost, var_list=c_vars)

            optimize = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(cost, var_list=c_vars)
            prediction_labels = tf.argmax(finaloutput, axis=1, name="output")
            read_labels = tf.argmax(input_labels, axis=1)

            correct_prediction = tf.equal(prediction_labels, read_labels)
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.int32))

            correct_times_in_batch = tf.reduce_sum(tf.cast(correct_prediction, tf.int32))

            return dict(
                x=input_data,
                y=input_labels,
                optimize=optimize,
                output=finaloutput,
                correct_prediction=correct_prediction,
                correct_times_in_batch=correct_times_in_batch,
                prediction_labels=prediction_labels,
                cost=cost
            )
