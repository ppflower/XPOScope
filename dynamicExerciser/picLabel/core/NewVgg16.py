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
import tensorflow as tf
from dynamicExerciser.picLabel.core import common as common, utils as utils
# import core.backbone as backbone
# from core.picLabel import YOLOV3
from dynamicExerciser.picLabel.core.config import cfg


class VGG16(object):
    """Implement tensoflow custmoized model to classify app scenarios here"""
    def __init__(self, input_data, input_labels, name):
        # 预训练参数
        self.yolo_classes     = utils.read_class_names(cfg.YOLO.CLASSES)  #类名
        self.yolo_num_class   = len(self.yolo_classes)  #类数量
        self.in_channel       = 3 * (self.yolo_num_class + 5)

        self.classes = ["APPStore", "camera", "Ebook", "express", "HouseRent", "job", "Live", "MapNavigation", "news", "OnlineCommunity", "OnlineTaxi", "SeHandCar", "ShopOnline", "ShortVideo", "TakeOut", "doctor", "MarryLove", "OnlineVideo", "travel", "browser", "ChildEducation", "hotel", "security", "sport", "TrafficTicket"]
        # self.classes = ["APPStore", "camera", "Ebook", "express", "HouseRent", "job", "Live", "MapNavigation", "news", "OnlineCommunity", "OnlineTaxi", "SeHandCar", "ShopOnline", "ShortVideo", "TakeOut"]
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video", "TakeOut", "shop_list", "APPshop_list"]  # TODO 通过读文件
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video"]
        self.num_class = len(self.classes)

        # try:
        self.model_vgg = self.__build_network_VGG16(input_data, input_labels, name)
        # self.model_resnet = self.__build_network_ResNet(input_data, input_labels, name)
        # except:
        #     raise NotImplementedError("Can not build up our customized network!")

    def __build_network_VGG16(self, input_data, input_labels, name):

        with tf.variable_scope(name):

            if name == 'vgg_sbbox':
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                                  trainable=True, name=name+'_downsamples0', downsample=True)
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                                  trainable=True, name=name+'_downsamples1', downsample=True)
            if name == 'vgg_lbbox':
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + 'convl0')
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + 'convl1')
                pass

            if name == 'vgg_mbbox':
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + 'convl0')
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                                  trainable=True, name=name+'_downsamplem0', downsample=True)

            # in_channel = 32
            # out_channel = 64

            input_data = common.convolutional(input_data=input_data,
                                              filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name='VGG_conv1', bn=True)
            input_data = common.convolutional(input_data=input_data,
                                              filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name='VGG_conv2', bn=True)
            input_data = common.convolutional(input_data=input_data,
                                              filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name='VGG_downsample1', downsample=True, bn=True)  # TODO max_pool

            # input_data = tf.nn.max_pool(input_data, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], 
            #                             padding='SAME', name='VGG_maxpool1')

            # in_channel = out_channel
            # out_channel = 128
            # input_data = common.convolutional(input_data=input_data, 
            #                                filters_shape=(3, 3, in_channel, out_channel), 
            #                                trainable=True, name='VGG_conv4', bn=True)
            # input_data = common.convolutional(input_data=input_data, 
            #                                filters_shape=(3, 3, out_channel, out_channel), 
            #                                trainable=True, name='VGG_conv5', bn=True)
            # input_data = common.convolutional(input_data=input_data, 
            #                                filters_shape=(3, 3, out_channel, out_channel), 
            #                                trainable=True, name='VGG_downsample2', downsample=True, bn=True)  # TODO max_pool

            # input_data = tf.nn.max_pool(input_data, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], 
            #                             padding='SAME', name='VGG_maxpool2')

            flatten = tf.keras.layers.Flatten()(input_data)
            output1 = tf.keras.layers.Dense(units=4096, use_bias=True, name='fc1', activation=lambda x : tf.nn.leaky_relu(x, alpha=0.1))(flatten)
            output2 = tf.keras.layers.Dense(units=4096, use_bias=True, name='fc2', activation=lambda x : tf.nn.leaky_relu(x, alpha=0.1))(output1)
            output = tf.keras.layers.Dense(units=self.num_class, use_bias=True, name='fc3', activation=None)(output2)

            finaloutput = tf.nn.softmax(output, name="softmax")

            cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=output, labels=input_labels))  #TODO

            all_vars = tf.global_variables()
            c_vars = [v for v in all_vars if v.name.split('/')[0].startswith(name)]
            # print(c_vars)
            # IPython.embed()

            # moving_ave = tf.train.ExponentialMovingAverage(0.9995).apply(c_vars)

            # with tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
            #     with tf.control_dependencies([moving_ave]):
            #         optimize = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(cost, var_list=c_vars)
                    # optimize = tf.train.AdadeltaOptimizer(learning_rate=1e-5, name="conv_all_op").minimize(cost, var_list=c_vars)

            optimize = tf.train.AdamOptimizer(learning_rate=1e-5).minimize(cost, var_list=c_vars)
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
                cost=cost,
                t_flat=flatten,
                t_fc1=output1,
                t_fc2=output2,
                t_fc3=output
            )



    def __build_network_ResNet(self, input_data, input_labels, name):

        with tf.variable_scope(name):

            if name=='resnet_sbbox':
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                                  trainable=True, name='convs0', downsample=True)
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                                  trainable=True, name='convs1', downsample=True)

            # if name=='resnet_lbbox':
              #   input_data = common.upsample(input_data, name=name+'_l0upsample', method="deconv")

            if name=='resnet_mbbox':
                input_data = common.convolutional(input_data, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                                  trainable=True, name='convm0', downsample=True)


            in_channel = self.in_channel
            out_channel =  self.in_channel #32
            input_data = common.convolutional(input_data=input_data,
                                              filters_shape=(3, 3, in_channel, out_channel),
                                              trainable=True, name='conv0', bn=True)

            in_channel = out_channel
            out_channel = self.in_channel #64
            input_data = common.yh_residual_block(input_data, in_channel, 32, in_channel, trainable=True, name='residual1')
            input_data = common.yh_residual_block(input_data, in_channel, 32, in_channel, trainable=True, name='residual2')
            input_data = common.convolutional(input_data, filters_shape=(3, 3, in_channel, out_channel),
                                              trainable=True, name='conv5', downsample=True)

            in_channel = out_channel
            out_channel = self.in_channel #128
            input_data = common.yh_residual_block(input_data, in_channel, 64, in_channel, trainable=True, name='residual3')
            input_data = common.yh_residual_block(input_data, in_channel, 64, in_channel, trainable=True, name='residual4')
            input_data = common.convolutional(input_data, filters_shape=(3, 3, in_channel, out_channel),
                                              trainable=True, name='conv10', downsample=True)

            # in_channel = out_channel
            # out_channel = self.in_channel #256
            # input_data = common.residual_block(input_data, in_channel,  128, in_channel, trainable=True, name='residual5')
            # input_data = common.residual_block(input_data, in_channel,  128, in_channel, trainable=True, name='residual6')
            # input_data = common.convolutional(input_data, filters_shape=(3, 3, in_channel, out_channel),
            #                               trainable=True, name='conv15', downsample=True)


            # input_data = tf.nn.avg_pool(input_data, [1, 2, 2, 1], strides=[1,1,1,1], padding='VALID')  # TODO
            flatten = tf.keras.layers.Flatten()(input_data)
            output = tf.keras.layers.Dense(units=1000, use_bias=True, name='fc2', activation='relu')(flatten)
            output = tf.keras.layers.Dense(units=self.num_class, use_bias=True, name='fc3', activation=None)(output)

            finaloutput = tf.nn.softmax(output, name="softmax")

            cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=output, labels=input_labels))  #TODO

            all_vars = tf.global_variables()
            c_vars = [v for v in all_vars if v.name.split('/')[0].startswith(name)]

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

















