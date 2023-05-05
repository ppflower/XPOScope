#! /usr/bin/env python
# coding=utf-8
# ================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   Editor      : VIM
#   File name   : picLabel.py
#   Author      : YunYang1994
#   Created date: 2019-02-28 10:47:03
#   Description :
#
# ================================================================

import numpy as np
import tensorflow.compat.v1 as tf
from dynamicExerciser.picLabel.core import backbone as backbone, common as common, utils as utils
from dynamicExerciser.picLabel.core.config import cfg

tf.disable_v2_behavior()

from dynamicExerciser import picLabel as MAP


class YOLOV3(object):
    """Implement tensoflow picLabel here"""

    def __init__(self, input_data, trainable):

        self.trainable = trainable
        self.classes = utils.read_class_names(cfg.YOLO.CLASSES)  # 类名
        self.num_class = len(self.classes)  # 类数量
        self.strides = np.array(cfg.YOLO.STRIDES)  # 步长之类的
        self.anchors = utils.get_anchors(cfg.YOLO.ANCHORS)  # 好像是检测的框框大小
        self.anchor_per_scale = cfg.YOLO.ANCHOR_PER_SCALE
        self.iou_loss_thresh = cfg.YOLO.IOU_LOSS_THRESH
        self.upsample_method = cfg.YOLO.UPSAMPLE_METHOD  # 现在是resize
        self.alpha = utils.get_alpha(cfg.YOLO.FOCALLOSS_ALPHA)

        try:
            self.conv_lbbox, self.conv_mbbox, self.conv_sbbox = self.__build_nework(input_data)  # 用于分类时应该是使用的这个输出
        except:
            raise NotImplementedError("Can not build up picLabel network!")

        with tf.variable_scope('pred_sbbox'):
            self.pred_sbbox = self.decode(self.conv_sbbox, self.anchors[0], self.strides[0])

        with tf.variable_scope('pred_mbbox'):
            self.pred_mbbox = self.decode(self.conv_mbbox, self.anchors[1], self.strides[1])

        with tf.variable_scope('pred_lbbox'):
            self.pred_lbbox = self.decode(self.conv_lbbox, self.anchors[2], self.strides[2])

    def __build_nework(self, input_data):

        route_1, route_2, input_data = backbone.darknet53(input_data, self.trainable)  # picLabel 的第一个结构

        input_data = common.convolutional(input_data, (1, 1, 1024, 512), self.trainable, 'conv52')  # 5层的DBL
        input_data = common.convolutional(input_data, (3, 3, 512, 1024), self.trainable, 'conv53')
        input_data = common.convolutional(input_data, (1, 1, 1024, 512), self.trainable, 'conv54')
        input_data = common.convolutional(input_data, (3, 3, 512, 1024), self.trainable, 'conv55')
        input_data = common.convolutional(input_data, (1, 1, 1024, 512), self.trainable, 'conv56')

        conv_lobj_branch = common.convolutional(input_data, (3, 3, 512, 1024), self.trainable, name='conv_lobj_branch')
        conv_lbbox = common.convolutional(conv_lobj_branch, (1, 1, 1024, 3 * (self.num_class + 5)),
                                          trainable=self.trainable, name='conv_lbbox', activate=False, bn=False)  # 生成y1

        input_data = common.convolutional(input_data, (1, 1, 512, 256), self.trainable, 'conv57')
        input_data = common.upsample(input_data, name='upsample0', method=self.upsample_method)

        with tf.variable_scope('route_1'):
            input_data = tf.concat([input_data, route_2], axis=-1)

        input_data = common.convolutional(input_data, (1, 1, 768, 256), self.trainable, 'conv58')
        input_data = common.convolutional(input_data, (3, 3, 256, 512), self.trainable, 'conv59')
        input_data = common.convolutional(input_data, (1, 1, 512, 256), self.trainable, 'conv60')
        input_data = common.convolutional(input_data, (3, 3, 256, 512), self.trainable, 'conv61')
        input_data = common.convolutional(input_data, (1, 1, 512, 256), self.trainable, 'conv62')

        conv_mobj_branch = common.convolutional(input_data, (3, 3, 256, 512), self.trainable, name='conv_mobj_branch')
        conv_mbbox = common.convolutional(conv_mobj_branch, (1, 1, 512, 3 * (self.num_class + 5)),
                                          trainable=self.trainable, name='conv_mbbox', activate=False, bn=False)  # 生成y2

        input_data = common.convolutional(input_data, (1, 1, 256, 128), self.trainable, 'conv63')
        input_data = common.upsample(input_data, name='upsample1', method=self.upsample_method)

        with tf.variable_scope('route_2'):
            input_data = tf.concat([input_data, route_1], axis=-1)

        input_data = common.convolutional(input_data, (1, 1, 384, 128), self.trainable, 'conv64')
        input_data = common.convolutional(input_data, (3, 3, 128, 256), self.trainable, 'conv65')
        input_data = common.convolutional(input_data, (1, 1, 256, 128), self.trainable, 'conv66')
        input_data = common.convolutional(input_data, (3, 3, 128, 256), self.trainable, 'conv67')
        input_data = common.convolutional(input_data, (1, 1, 256, 128), self.trainable, 'conv68')

        conv_sobj_branch = common.convolutional(input_data, (3, 3, 128, 256), self.trainable, name='conv_sobj_branch')
        conv_sbbox = common.convolutional(conv_sobj_branch, (1, 1, 256, 3 * (self.num_class + 5)),
                                          trainable=self.trainable, name='conv_sbbox', activate=False, bn=False)  # 生成y3

        return conv_lbbox, conv_mbbox, conv_sbbox

    def decode(self, conv_output, anchors, stride):  # 后面应该实在检测物体了
        """
        return tensor of shape [batch_size, output_size, output_size, anchor_per_scale, 5 + num_classes]
               contains (x, y, w, h, score, probability)
        """

        conv_shape = tf.shape(conv_output)
        batch_size = conv_shape[0]
        # TODO by zhangz 修改尺寸
        # output_size      = conv_shape[1]
        output_size_h = conv_shape[1]
        output_size_w = conv_shape[2]
        anchor_per_scale = len(anchors)

        # conv_output = tf.reshape(conv_output, (batch_size, output_size, output_size, anchor_per_scale, 5 + self.num_class))
        conv_output = tf.reshape(conv_output,
                                 (batch_size, output_size_h, output_size_w, anchor_per_scale, 5 + self.num_class))

        conv_raw_dxdy = conv_output[:, :, :, :, 0:2]
        conv_raw_dwdh = conv_output[:, :, :, :, 2:4]
        conv_raw_conf = conv_output[:, :, :, :, 4:5]
        conv_raw_prob = conv_output[:, :, :, :, 5:]

        # TODO by zhangz 修改尺寸
        # y = tf.tile(tf.range(output_size, dtype=tf.int32)[:, tf.newaxis], [1, output_size])
        # x = tf.tile(tf.range(output_size, dtype=tf.int32)[tf.newaxis, :], [output_size, 1])

        y = tf.tile(tf.range(output_size_h, dtype=tf.int32)[:, tf.newaxis], [1, output_size_w])
        x = tf.tile(tf.range(output_size_w, dtype=tf.int32)[tf.newaxis, :], [output_size_h, 1])

        xy_grid = tf.concat([x[:, :, tf.newaxis], y[:, :, tf.newaxis]], axis=-1)
        xy_grid = tf.tile(xy_grid[tf.newaxis, :, :, tf.newaxis, :], [batch_size, 1, 1, anchor_per_scale, 1])
        xy_grid = tf.cast(xy_grid, tf.float32)

        pred_xy = (tf.sigmoid(conv_raw_dxdy) + xy_grid) * stride
        pred_wh = (tf.exp(conv_raw_dwdh) * anchors) * stride
        pred_xywh = tf.concat([pred_xy, pred_wh], axis=-1)

        pred_conf = tf.sigmoid(conv_raw_conf)  # 计算框或者应该说是网格线中存在物体的置信度
        pred_prob = tf.sigmoid(conv_raw_prob)  # 预测框里object类别概率

        return tf.concat([pred_xywh, pred_conf, pred_prob], axis=-1)

    def focal(self, target, actual, alpha=1, gamma=2):
        focal_loss = alpha * tf.pow(tf.abs(target - actual), gamma)
        # focal_loss = tf.abs(alpha + target -1) * tf.pow(tf.abs(target - actual), gamma)
        return focal_loss

    def my_focal(self, target, actual, gamma=2):
        # TODO 
        # focal_loss = - target * tf.pow(1 - actual, gamma) * tf.log(actual)  
        # focal_loss = tf.pow(1-target*actual, gamma)
        weight = tf.multiply(target, tf.pow(tf.subtract(1., actual), gamma))
        if self.alpha != 0.0:
            alpha_t = target * self.alpha + (tf.ones_like(target) - target) * (tf.ones_like(target) - self.alpha)
        # else:
        alpha_t = tf.ones_like(target)  # alpha换成数组，数组长度和类别总数相同，每个元素表示对应类别的权重
        xent = tf.multiply(target, -tf.log(actual))  # 原始交叉熵
        focal_xent = tf.multiply(alpha_t, tf.multiply(weight, xent))
        # focal_loss = target * tf.pow(1 - actual, gamma)
        return focal_xent

    def bbox_giou(self, boxes1, boxes2):

        boxes1 = tf.concat([boxes1[..., :2] - boxes1[..., 2:] * 0.5,
                            boxes1[..., :2] + boxes1[..., 2:] * 0.5], axis=-1)
        boxes2 = tf.concat([boxes2[..., :2] - boxes2[..., 2:] * 0.5,
                            boxes2[..., :2] + boxes2[..., 2:] * 0.5], axis=-1)

        boxes1 = tf.concat([tf.minimum(boxes1[..., :2], boxes1[..., 2:]),
                            tf.maximum(boxes1[..., :2], boxes1[..., 2:])], axis=-1)
        boxes2 = tf.concat([tf.minimum(boxes2[..., :2], boxes2[..., 2:]),
                            tf.maximum(boxes2[..., :2], boxes2[..., 2:])], axis=-1)

        boxes1_area = (boxes1[..., 2] - boxes1[..., 0]) * (boxes1[..., 3] - boxes1[..., 1])
        boxes2_area = (boxes2[..., 2] - boxes2[..., 0]) * (boxes2[..., 3] - boxes2[..., 1])

        left_up = tf.maximum(boxes1[..., :2], boxes2[..., :2])
        right_down = tf.minimum(boxes1[..., 2:], boxes2[..., 2:])

        inter_section = tf.maximum(right_down - left_up, 0.0)
        inter_area = inter_section[..., 0] * inter_section[..., 1]
        union_area = boxes1_area + boxes2_area - inter_area
        iou = inter_area / union_area

        enclose_left_up = tf.minimum(boxes1[..., :2], boxes2[..., :2])
        enclose_right_down = tf.maximum(boxes1[..., 2:], boxes2[..., 2:])
        enclose = tf.maximum(enclose_right_down - enclose_left_up, 0.0)
        enclose_area = enclose[..., 0] * enclose[..., 1]
        giou = iou - 1.0 * (enclose_area - union_area) / enclose_area

        return giou

    def bbox_iou(self, boxes1, boxes2):

        boxes1_area = boxes1[..., 2] * boxes1[..., 3]
        boxes2_area = boxes2[..., 2] * boxes2[..., 3]

        boxes1 = tf.concat([boxes1[..., :2] - boxes1[..., 2:] * 0.5,
                            boxes1[..., :2] + boxes1[..., 2:] * 0.5], axis=-1)
        boxes2 = tf.concat([boxes2[..., :2] - boxes2[..., 2:] * 0.5,
                            boxes2[..., :2] + boxes2[..., 2:] * 0.5], axis=-1)

        left_up = tf.maximum(boxes1[..., :2], boxes2[..., :2])
        right_down = tf.minimum(boxes1[..., 2:], boxes2[..., 2:])

        inter_section = tf.maximum(right_down - left_up, 0.0)
        inter_area = inter_section[..., 0] * inter_section[..., 1]
        union_area = boxes1_area + boxes2_area - inter_area
        iou = 1.0 * inter_area / union_area

        return iou

    def loss_layer(self, conv, pred, label, bboxes, anchors, stride):

        conv_shape = tf.shape(conv)
        batch_size = conv_shape[0]
        output_size = conv_shape[1]
        input_size = stride * output_size
        conv = tf.reshape(conv, (batch_size, output_size, output_size,
                                 self.anchor_per_scale, 5 + self.num_class))
        conv_raw_conf = conv[:, :, :, :, 4:5]
        conv_raw_prob = conv[:, :, :, :, 5:]

        pred_xywh = pred[:, :, :, :, 0:4]
        pred_conf = pred[:, :, :, :, 4:5]
        # TODO
        pred_prob = pred[:, :, :, :, 5:]

        label_xywh = label[:, :, :, :, 0:4]
        respond_bbox = label[:, :, :, :, 4:5]  # 置信度判断框内有无物体
        label_prob = label[:, :, :, :, 5:]

        giou = tf.expand_dims(self.bbox_giou(pred_xywh, label_xywh), axis=-1)
        input_size = tf.cast(input_size, tf.float32)

        bbox_loss_scale = 2.0 - 1.0 * label_xywh[:, :, :, :, 2:3] * label_xywh[:, :, :, :, 3:4] / (input_size ** 2)
        giou_loss = respond_bbox * bbox_loss_scale * (
                    1 - giou)  # giou_loss使得giou越大越好，即预测框与真实框之间的重叠度， bbox_loss_scale为了弱化边界框大小对giou_loss的影响

        iou = self.bbox_iou(pred_xywh[:, :, :, :, np.newaxis, :], bboxes[:, np.newaxis, np.newaxis, np.newaxis, :, :])
        max_iou = tf.expand_dims(tf.reduce_max(iou, axis=-1), axis=-1)

        respond_bgd = (1.0 - respond_bbox) * tf.cast(max_iou < self.iou_loss_thresh, tf.float32)  # 判断框是不是背景

        conf_focal = self.focal(respond_bbox, pred_conf)

        conf_loss = conf_focal * (
                respond_bbox * tf.nn.sigmoid_cross_entropy_with_logits(labels=respond_bbox, logits=conv_raw_conf)
                +
                respond_bgd * tf.nn.sigmoid_cross_entropy_with_logits(labels=respond_bbox, logits=conv_raw_conf)
        )
        # TODO
        # prob_loss = self.my_focal(label_prob, pred_prob)
        # prob_loss = prob_loss * respond_bbox * tf.nn.sigmoid_cross_entropy_with_logits(labels=label_prob, logits=conv_raw_prob)
        prob_loss = respond_bbox * tf.nn.sigmoid_cross_entropy_with_logits(labels=label_prob,
                                                                           logits=conv_raw_prob)  # 是需要改为focal loss
        giou_loss = tf.reduce_mean(tf.reduce_sum(giou_loss, axis=[1, 2, 3, 4]))  # 框回顾损失
        conf_loss = tf.reduce_mean(
            tf.reduce_sum(conf_loss, axis=[1, 2, 3, 4]))  # 置信度损失，这里就是用的focal loss，先计算交叉熵的权重因子再乘的ce
        prob_loss = tf.reduce_mean(tf.reduce_sum(prob_loss, axis=[1, 2, 3, 4]))  # 分类损失, 视为两分类，本类和其他类

        return giou_loss, conf_loss, prob_loss

    def compute_loss(self, label_sbbox, label_mbbox, label_lbbox, true_sbbox, true_mbbox, true_lbbox):

        with tf.name_scope('smaller_box_loss'):
            loss_sbbox = self.loss_layer(self.conv_sbbox, self.pred_sbbox, label_sbbox, true_sbbox,
                                         anchors=self.anchors[0], stride=self.strides[0])

        with tf.name_scope('medium_box_loss'):
            loss_mbbox = self.loss_layer(self.conv_mbbox, self.pred_mbbox, label_mbbox, true_mbbox,
                                         anchors=self.anchors[1], stride=self.strides[1])

        with tf.name_scope('bigger_box_loss'):
            loss_lbbox = self.loss_layer(self.conv_lbbox, self.pred_lbbox, label_lbbox, true_lbbox,
                                         anchors=self.anchors[2], stride=self.strides[2])

        with tf.name_scope('giou_loss'):
            giou_loss = loss_sbbox[0] + loss_mbbox[0] + loss_lbbox[0]

        with tf.name_scope('conf_loss'):
            conf_loss = loss_sbbox[1] + loss_mbbox[1] + loss_lbbox[1]

        with tf.name_scope('prob_loss'):
            prob_loss = loss_sbbox[2] + loss_mbbox[2] + loss_lbbox[2]

        return giou_loss, conf_loss, prob_loss

    def compute_MAP(self, groud_truth, size):  # 不能把这个计算放在网络中
        min_overlap = 0.5

        sum_AP = 0.0
        batchsize = cfg.TEST.BATCH_SIZE

        for num in range(batchsize):

            groud_box = MAP.get_ground_truth(groud_truth[num])
            org_w, org_h = size[0], size[1]
            pred_bbox = np.concatenate([np.reshape(self.pred_sbbox[num], (-1, 5 + 2)),
                                        np.reshape(self.pred_mbbox[num], (-1, 5 + 2)),
                                        np.reshape(self.pred_lbbox[num], (-1, 5 + 2))], axis=0)
            bboxes = utils.postprocess_boxes(pred_bbox, (org_h, org_w), 512,
                                             self.score_threshold)  # 返回原本图像大小的框并且去掉分数小于阈值的框
            bboxes = utils.nms(bboxes, self.iou_threshold)  # nms抑制的处理
            bbox_predict = []
            for bbox in bboxes:
                coor = np.array(bbox[:4], dtype=np.int32)
                score = bbox[4]
                class_ind = int(bbox[5])
                class_name = self.classes[class_ind]
                score = '%.4f' % score
                xmin, ymin, xmax, ymax = list(map(str, coor))
                bbox_predict.append([class_name, score, xmin, ymin, xmax, ymax])

            bbox_predict.sort(key=lambda x: float(x[1]), reverse=True)
            tp = [0] * len(bbox_predict)
            fp = [0] * len(bbox_predict)

            for idx, bb in enumerate(bbox_predict):
                ovmax = -1
                gt_match = -1
                for bbgt in groud_box:
                    if bb[0] == bbgt[0]:
                        bi = [max(bb[2], bbgt[2]), max(bb[3], bbgt[3]), min(bb[4], bbgt[4]), min(bb[5], bbgt[5])]
                        iw = bi[4] - bi[2] + 1
                        ih = bi[5] - bi[3] + 1
                        if iw > 0 and ih > 0:
                            ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + (bbgt[2] - bbgt[0]
                                                                              + 1) * (bbgt[3] - bbgt[1] + 1) - iw * ih
                            ov = iw * ih / ua
                            if ov > ovmax:
                                ovmax = ov
                                gt_match = bbgt
                if ovmax >= min_overlap:
                    if gt_match[1] == 0:
                        tp[idx] = 1
                        gt_match[1] = 1
                    else:
                        fp[idx] = 1
                else:
                    fp[idx] = 1

            cumsum = 0
            for idx, val in enumerate(fp):
                fp[idx] += cumsum
                cumsum += val
            cumsum = 0
            for idx, val in enumerate(tp):
                tp[idx] += cumsum
                cumsum += val
            rec = tp[:]
            for idx, val in enumerate(tp):
                rec[idx] = float(tp[idx]) / len(groud_box)
            prec = tp[:]
            for idx, val in enumerate(tp):
                prec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])
            ap, mrec, mprec = MAP.voc_ap(rec, prec)
            sum_AP += ap
        mAP = sum_AP / batchsize
        return mAP * 100
