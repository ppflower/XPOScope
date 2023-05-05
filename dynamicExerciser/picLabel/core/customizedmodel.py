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
from dynamicExerciser.picLabel.core.vgg16_testonecls import VGG16 as VGG17
from dynamicExerciser.picLabel.core.vgg16 import VGG16
from dynamicExerciser.picLabel.core import config as cfg


class CustomizedModel(object):
    """Implement tensoflow custmoized model to classify app scenarios here"""
    def __init__(self, input_data, input_labels, input_text_ex, trainable):
        # 预训练参数
        self.yolo_classes     = utils.read_class_names(cfg.YOLO.CLASSES)  #类名
        self.yolo_num_class   = len(self.yolo_classes)  #类数量
        self.in_channel       = 3 * (self.yolo_num_class + 5) + 52

        self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video", "TakeOut", "shop_list", "APPshop_list"]
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video"]
        self.num_class = len(self.classes)

        try:
            self.combineembedding = self.__build_network(input_data, input_labels, trainable, input_text_ex)
        except:
            raise NotImplementedError("Can not build up our customized network!")

    def __build_network(self, input_data, input_labels, trainable, input_text_ex): 
        yolo             = yolov3(input_data, trainable) #初始化yolo，作为我们的前缀网络结构
        conv_lbbox       = yolo.conv_lbbox  #y1 [13, 13, ?]
        conv_mbbox       = yolo.conv_mbbox  #y2 [26, 26, ?]
        conv_sbbox       = yolo.conv_sbbox  #y3用于分类时应该是使用的这个输出 [52, 52, ?]
        
        conv_sbbox = tf.concat([conv_sbbox, input_text_ex], axis=-1)
        conv_mbbox = tf.concat([conv_mbbox, input_text_ex[:, :32, :32, :]], axis=-1)
        conv_lbbox = tf.concat([conv_lbbox, input_text_ex[:, :16, :16, :]], axis=-1)

        sbbox_output = VGG16(conv_sbbox, input_labels, 'vgg_sbbox').model
        lbbox_output = VGG16(conv_lbbox, input_labels, 'vgg_lbbox').model
        mbbox_output = VGG16(conv_mbbox, input_labels, 'vgg_mbbox').model

        # TODO change 
        mixbox_output = VGG17(conv_lbbox, conv_mbbox, conv_sbbox, input_labels, 'vgg_mixbox').model

        # with tf.variable_scope("fin_fc"):
        #     all_output = np.concatenate

        # all_softmax_output = lbbox_output['output'] + mbbox_output['output'] + sbbox_output['output']
        # all_cost = lbbox_output['cost'] + mbbox_output['cost'] + sbbox_output['cost']

        all_softmax_output = lbbox_output['output'] + mbbox_output['output'] + sbbox_output['output'] + mixbox_output['output'] 
        all_cost = lbbox_output['cost'] + mbbox_output['cost'] + sbbox_output['cost'] + mixbox_output['cost']

        all_3_softmax_output = lbbox_output['output'] + mbbox_output['output'] + sbbox_output['output']
        all_3_cost = lbbox_output['cost'] + mbbox_output['cost'] + sbbox_output['cost']

        # 线性优化
        # with tf.variable_scope("dy_weight"):
        #     w1 = tf.Variable(tf.random_uniform([1], 0, 0.5), dtype=tf.float32)
        #     w2 = tf.Variable(tf.random_uniform([1], 0, 0.5), dtype=tf.float32)
        #     linear = w1 * lbbox_output['output'] + w2 * mbbox_output['output'] + (1 - w1 - w2) * sbbox_output['output']
        #     linearloss = tf.reduce_sum(tf.square(linear - input_labels))
        #     all_vars = tf.global_variables()
        #     c_vars = [v for v in all_vars if v.name.split('/')[0].startswith("dy_weight")]
        #     woptimize = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(linearloss, var_list=c_vars)
            
        #     prediction_lin_labels = tf.argmax(linear, axis=1, name="linear_output")
        
        # with tf.control_dependencies([lbbox_output['optimize'], mbbox_output['optimize'], sbbox_output['optimize']]):
            # all_optimize = tf.no_op()

        prediction_labels = tf.argmax(all_softmax_output, axis=1, name="output")
        prediction_3_labels = tf.argmax(all_3_softmax_output, axis=1, name="3output")

        read_labels = tf.argmax(input_labels, axis=1)

        correct_prediction = tf.equal(prediction_labels, read_labels)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.int32))
        correct_times_in_batch = tf.reduce_sum(tf.cast(correct_prediction, tf.int32))

        correct_prediction_3 = tf.equal(prediction_3_labels, read_labels)
        accuracy_3 = tf.reduce_mean(tf.cast(correct_prediction_3, tf.int32))
        correct_times_in_batch_3 = tf.reduce_sum(tf.cast(correct_prediction_3, tf.int32))

        # correct_prediction_l = tf.equal(prediction_lin_labels, read_labels)
        # accuracy_l = tf.reduce_mean(tf.cast(correct_prediction_l, tf.int32))
        # correct_times_in_batch_l = tf.reduce_sum(tf.cast(correct_prediction_l, tf.int32))

        return dict(
            x=input_data,
            y=input_labels,
            x2=input_text_ex,
            # optimize=all_optimize,
            moptimize=mbbox_output['optimize'],
            loptimize=lbbox_output['optimize'],
            soptimize=sbbox_output['optimize'],
            # TODO
            mixoptimize=mixbox_output['optimize'],
            # woptimize=woptimize,
            # lbbox_out
            l_out=dict(
                cost=lbbox_output['cost'],
                correct_prediction=lbbox_output['correct_prediction'],
                correct_times_in_batch=lbbox_output['correct_times_in_batch'],
                prediction_labels=lbbox_output['prediction_labels']
            ),
            # mbbox_out
            m_out=dict(
                cost=mbbox_output['cost'],
                correct_prediction=mbbox_output['correct_prediction'],
                correct_times_in_batch=mbbox_output['correct_times_in_batch'],
                prediction_labels=mbbox_output['prediction_labels']
            ),
            # sbbox_out
            s_out=dict(
                cost=sbbox_output['cost'],
                correct_prediction=sbbox_output['correct_prediction'],
                correct_times_in_batch=sbbox_output['correct_times_in_batch'],
                prediction_labels=sbbox_output['prediction_labels']
            ),
            # TODO
            mix_out=dict(
                cost=mixbox_output['cost'],
                correct_prediction=mixbox_output['correct_prediction'],
                correct_times_in_batch=mixbox_output['correct_times_in_batch'],
                prediction_labels=mixbox_output['prediction_labels']
            ),
            # fin_out
            fin_out=dict(
                cost=all_cost,
                correct_prediction=correct_prediction,
                correct_times_in_batch=correct_times_in_batch,
                prediction_labels=prediction_labels
            ),
            fin_3_out=dict(
                cost=all_3_cost,
                correct_prediction=correct_prediction_3,
                correct_times_in_batch=correct_times_in_batch_3,
                prediction_labels=prediction_3_labels
            ),
            # fin_l_out=dict(
            #     cost=all_3_cost,
            #     correct_prediction=correct_prediction_l,
            #     correct_times_in_batch=correct_times_in_batch_l,
            #     prediction_labels=prediction_lin_labels
            # )
        )

    def fc_layer(self, inputtf, input_size, output_size, name):

        if input_size is None:
            input_size = int(np.prod(inputtf.get_shape()[1:]))
            inputtf = tf.reshape(inputtf, [-1, input_size])

        kernel = tf.Variable(tf.truncated_normal([input_size, output_size], dtype=tf.float32, stddev=0.1))
        biases = tf.Variable(tf.constant(0.1, dtype=tf.float32, shape=[output_size]))
        
        output = tf.nn.relu(tf.matmul(inputtf, kernel) + biases, name=name)

        return output

