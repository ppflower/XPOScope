#! /usr/bin/env python
# coding=utf-8
#================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   Editor      : VIM
#   File name   : backbone.py
#   Author      : YunYang1994
#   Created date: 2019-02-17 11:03:35
#   Description :
#
#================================================================

from dynamicExerciser.picLabel.core import common as common
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()

def darknet53(input_data, trainable):

    with tf.variable_scope('darknet'):  #和name_scope差不多

        input_data = common.convolutional(input_data, filters_shape=(3, 3, 3, 32), trainable=trainable, name='conv0') #卷积层，卷积核尺寸3X3X3，数量32----DBL层
        input_data = common.convolutional(input_data, filters_shape=(3, 3, 32, 64),
                                          trainable=trainable, name='conv1', downsample=True)  #zeropadding + DBL

        for i in range(1):
            input_data = common.residual_block(input_data, 64, 32, 64, trainable=trainable, name='residual%d' % (i + 0))  #res1层

        input_data = common.convolutional(input_data, filters_shape=(3, 3, 64, 128),
                                          trainable=trainable, name='conv4', downsample=True)   

        for i in range(2):
            input_data = common.residual_block(input_data, 128, 64, 128, trainable=trainable, name='residual%d' % (i + 1))  #res2
 
        input_data = common.convolutional(input_data, filters_shape=(3, 3, 128, 256),
                                          trainable=trainable, name='conv9', downsample=True)

        for i in range(8):
            input_data = common.residual_block(input_data, 256, 128, 256, trainable=trainable, name='residual%d' % (i + 3))  #res8

        route_1 = input_data
        input_data = common.convolutional(input_data, filters_shape=(3, 3, 256, 512),
                                          trainable=trainable, name='conv26', downsample=True)

        for i in range(8):
            input_data = common.residual_block(input_data, 512, 256, 512, trainable=trainable, name='residual%d' % (i + 11))  #res8，后面算解码器部分了吗？

        route_2 = input_data
        input_data = common.convolutional(input_data, filters_shape=(3, 3, 512, 1024),
                                          trainable=trainable, name='conv43', downsample=True)

        for i in range(4):  
            input_data = common.residual_block(input_data, 1024, 512, 1024, trainable=trainable, name='residual%d' % (i + 19)) #res4

        return route_1, route_2, input_data




