import numpy as np
import tensorflow as tf
from dynamicExerciser.picLabel.core import common as common, utils as utils
# import core.backbone as backbone
from dynamicExerciser.picLabel.core.yolov3 import YOLOV3
from dynamicExerciser.picLabel.core.NewVgg16 import VGG16
from dynamicExerciser.picLabel.core.config import cfg


class CustomizedModel(object):
    """Implement tensoflow custmoized model to classify app scenarios here"""
    def __init__(self, input_data, input_labels, trainable):
        # 预训练参数
        self.yolo_classes     = utils.read_class_names(cfg.YOLO.CLASSES)  #类名
        self.yolo_num_class   = len(self.yolo_classes)  #类数量
        self.in_channel       = 3 * (self.yolo_num_class + 5)

        self.classes = ["APPStore", "camera", "Ebook", "express", "HouseRent", "job", "Live", "MapNavigation", "news", "OnlineCommunity", "OnlineTaxi", "SeHandCar", "ShopOnline", "ShortVideo", "TakeOut", "doctor", "MarryLove", "OnlineVideo", "travel", "browser", "ChildEducation", "hotel", "security", "sport", "TrafficTicket"]
        # self.classes = ["APPStore", "camera", "Ebook", "express", "HouseRent", "job", "Live", "MapNavigation", "news", "OnlineCommunity", "OnlineTaxi", "SeHandCar", "ShopOnline", "ShortVideo", "TakeOut"]
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video", "TakeOut", "shop_list", "APPshop_list"]
        # self.classes = ["camera", "login", "map", "news", "permission", "scan", "short_video"]
        self.num_class = len(self.classes)

        
        self.combineembedding = self.__build_network(input_data, input_labels, trainable)
        # except Exception as e:
        #     raise NotImplementedError("Can not build up our customized network!")

    


    def __build_network(self, input_data, input_labels, trainable): 
        yolo             = YOLOV3(input_data, trainable) #初始化yolo，作为我们的前缀网络结构
        conv_lbbox       = yolo.conv_lbbox  #y1 [16, 16, ?]
        conv_mbbox       = yolo.conv_mbbox  #y2 [32, 32, ?]
        conv_sbbox       = yolo.conv_sbbox  #y3用于分类时应该是使用的这个输出 [64, 64, ?]

        # 两两融合
        # conv_smbbox = self.mergebox(conv_sbbox=conv_sbbox, conv_mbbox=conv_mbbox, name='merge_sm')
        # conv_slbbox = self.mergebox(conv_sbbox=conv_sbbox, conv_lbbox=conv_lbbox, name='merge_sl')
        # conv_mlbbox = self.mergebox(conv_mbbox=conv_mbbox, conv_lbbox=conv_lbbox, name='merge_ml')


        # conv_smbbox = self.mergebox_new(conv_sbbox=conv_sbbox, conv_mbbox=conv_mbbox, name='merge_sm')
        # conv_slbbox = self.mergebox_new(conv_sbbox=conv_sbbox, conv_lbbox=conv_lbbox, name='merge_sl')
        # conv_mlbbox = self.mergebox_new(conv_mbbox=conv_mbbox, conv_lbbox=conv_lbbox, name='merge_ml')

        # 三个融合
        # conv_smlbbox = self.mergebox(conv_sbbox=conv_sbbox, conv_mbbox = conv_mbbox, conv_lbbox = conv_lbbox, name='merge_sml')

        conv_smlbbox = self.mergebox_new(conv_sbbox=conv_sbbox, conv_mbbox = conv_mbbox, conv_lbbox = conv_lbbox, name='merge_sml')

        # 7 个VGG网络分别训练
        sbbox_output = VGG16(conv_sbbox, input_labels, 'vgg_sbbox').model_vgg    # 64 X 64
        lbbox_output = VGG16(conv_lbbox, input_labels, 'vgg_lbbox').model_vgg    # 16 X 16
        mbbox_output = VGG16(conv_mbbox, input_labels, 'vgg_mbbox').model_vgg    # 32 X 32
        # smbbox_output = VGG16(conv_smbbox, input_labels, 'vgg_smbbox').model_vgg # 16 X 16
        # slbbox_output = VGG16(conv_slbbox, input_labels, 'vgg_slbbox').model_vgg # 16 X 16
        # mlbbox_output = VGG16(conv_mlbbox, input_labels, 'vgg_mlbbox').model_vgg # 16 X 16
        smlbbox_output = VGG16(conv_smlbbox, input_labels, 'vgg_smlbbox').model_vgg # 16 X 16

        # 7个resnet网络分别训练
        # sbbox_output = VGG16(conv_sbbox, input_labels, 'resnet_sbbox').model_resnet
        # lbbox_output = VGG16(conv_lbbox, input_labels, 'resnet_lbbox').model_resnet
        # mbbox_output = VGG16(conv_mbbox, input_labels, 'resnet_mbbox').model_resnet
        # smbbox_output = VGG16(conv_smbbox, input_labels, 'resnet_smbbox').model_resnet
        # slbbox_output = VGG16(conv_slbbox, input_labels, 'resnet_slbbox').model_resnet
        # mlbbox_output = VGG16(conv_mlbbox, input_labels, 'resnet_mlbbox').model_resnet
        # smlbbox_output = VGG16(conv_smlbbox, input_labels, 'resnet_smlbbox').model_resnet



        # all_softmax_output = smbbox_output['output'] + slbbox_output['output'] + mlbbox_output['output']
        all_softmax_output = lbbox_output['output'] + mbbox_output['output'] + sbbox_output['output'] + smlbbox_output['output']  # 
        # all_cost = smbbox_output['cost'] + slbbox_output['cost'] + mlbbox_output['cost']
        all_cost = lbbox_output['cost'] + mbbox_output['cost'] + sbbox_output['cost'] + smlbbox_output['cost']

        prediction_labels = tf.argmax(all_softmax_output, axis=1, name="output")
        read_labels = tf.argmax(input_labels, axis=1)
        correct_prediction = tf.equal(prediction_labels, read_labels)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.int32))
        correct_times_in_batch = tf.reduce_sum(tf.cast(correct_prediction, tf.int32))


        # all_softmax_output_nsl = lbbox_output['output'] + mbbox_output['output'] + sbbox_output['output'] + smbbox_output['output'] + mlbbox_output['output'] + smlbbox_output['output'] # SL不参与投票
        # prediction_labels_nsl = tf.argmax(all_softmax_output_nsl, axis=1, name="output")
        # correct_prediction_nsl = tf.equal(prediction_labels_nsl, read_labels)
        # correct_times_in_batch_nsl = tf.reduce_sum(tf.cast(correct_prediction_nsl, tf.int32))



        # correct_prediction_3 = tf.equal(prediction_3_labels, read_labels)
        # accuracy_3 = tf.reduce_mean(tf.cast(correct_prediction_3, tf.int32))
        # correct_times_in_batch_3 = tf.reduce_sum(tf.cast(correct_prediction_3, tf.int32))

        # correct_prediction_l = tf.equal(prediction_lin_labels, read_labels)
        # accuracy_l = tf.reduce_mean(tf.cast(correct_prediction_l, tf.int32))
        # correct_times_in_batch_l = tf.reduce_sum(tf.cast(correct_prediction_l, tf.int32))

        return dict(
            x=input_data,
            y=input_labels,
            # optimize=all_optimize,
            moptimize=mbbox_output['optimize'],
            loptimize=lbbox_output['optimize'],
            soptimize=sbbox_output['optimize'],
            # smoptimize=smbbox_output['optimize'],
            # sloptimize=slbbox_output['optimize'],
            # mloptimize=mlbbox_output['optimize'],
            smloptimize=smlbbox_output['optimize'],
            # TODO
            # bbox output
            # lbbox_out
            l_out=dict(
                cost=lbbox_output['cost'],
                correct_prediction=lbbox_output['correct_prediction'],
                correct_times_in_batch=lbbox_output['correct_times_in_batch'],
                prediction_labels=lbbox_output['prediction_labels'],
                t_lboxfea = conv_lbbox,
                t_convres = lbbox_output['x'],
                t_flat = lbbox_output['t_flat'],
                t_fc1 = lbbox_output['t_fc1'],
                t_fc2 = lbbox_output['t_fc2'],
                t_fc3 = lbbox_output['t_fc3'],
                t_softoutput = lbbox_output['output'],
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
            # sm_out=dict(
            #     cost=smbbox_output['cost'],
            #     correct_prediction=smbbox_output['correct_prediction'],
            #     correct_times_in_batch=smbbox_output['correct_times_in_batch'],
            #     prediction_labels=smbbox_output['prediction_labels']
            # ),
            # sl_out=dict(
            #     cost=slbbox_output['cost'],
            #     correct_prediction=slbbox_output['correct_prediction'],
            #     correct_times_in_batch=slbbox_output['correct_times_in_batch'],
            #     prediction_labels=slbbox_output['prediction_labels']
            # ),
            # ml_out=dict(
            #     cost=mlbbox_output['cost'],
            #     correct_prediction=mlbbox_output['correct_prediction'],
            #     correct_times_in_batch=mlbbox_output['correct_times_in_batch'],
            #     prediction_labels=mlbbox_output['prediction_labels']
            # ),
            sml_out=dict(
                cost=smlbbox_output['cost'],
                correct_prediction=smlbbox_output['correct_prediction'],
                correct_times_in_batch=smlbbox_output['correct_times_in_batch'],
                prediction_labels=smlbbox_output['prediction_labels']
            ),
            # fin_out
            # fin_nsl_out=dict(
            #     cost=all_cost,
            #     correct_prediction=correct_prediction_nsl,
            #     correct_times_in_batch=correct_times_in_batch_nsl,
            #     prediction_labels=prediction_labels_nsl
            # ),
            
            fin_out=dict(
                all_softmax=all_softmax_output,
                cost=all_cost,
                correct_prediction=correct_prediction,
                correct_times_in_batch=correct_times_in_batch,
                prediction_labels=prediction_labels
            ),

            # softmax = dict(
            #     all_softmax_output = all_softmax_output,
            #     lbbox_softmax = lbbox_output['output'],
            #     mbbox_softmax = mbbox_output['output'],
            #     sbbox_softmax = sbbox_output['output'],
            #     smbbox_softmax = smbbox_output['output'],
            #     slbbox_softmax = slbbox_output['output'],
            #     mlbbox_softmax = mlbbox_output['output'],
            #     smlbbox_softmax = smlbbox_output['output']
            # )


        )


    def mergebox(self, conv_sbbox=None, conv_mbbox=None, conv_lbbox=None, name=None):
        if conv_lbbox != None:
            conv_lbbox = common.upsample(conv_lbbox, name=name + '_upsample', method="deconv")
        else:
            # conv_lbbox = tf.zeros([1, 32, 32, self.in_channel])  # TODO 硬写入的形状，后面可能会改
            conv_lbbox = np.zeros_like(conv_mbbox, dtype='float32')
        
        if conv_mbbox != None:
            conv_mbbox = conv_mbbox
        else:
            # conv_mbbox = tf.zeros([1, 32, 32, self.in_channel])
            conv_mbbox = np.zeros_like(conv_mbbox, dtype='float32')
        

        if conv_sbbox != None:
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsample', downsample=True)
        else:
            # conv_sbbox = tf.zeros([1, 32, 32, self.in_channel])
            conv_sbbox = np.zeros_like(conv_sbbox, dtype='float32')
        return conv_lbbox + conv_mbbox + conv_sbbox


      
    def mergebox_new(self, conv_sbbox=None, conv_mbbox=None, conv_lbbox=None, name=None):
        if name == 'merge_sm':
            conv_mbbox = common.convolutional(conv_mbbox, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + '_downsamplesm0', downsample=True)
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamples0', downsample=True)
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamples1', downsample=True)
            return conv_mbbox + conv_sbbox
        
        if name == 'merge_sl':
            conv_lbbox = common.convolutional(conv_lbbox, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + 'convl1')
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamples0', downsample=True)
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamples1', downsample=True)
            return conv_lbbox + conv_sbbox
        

        if name == 'merge_ml':
            conv_lbbox = common.convolutional(conv_lbbox, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + 'convl0')
            conv_mbbox = common.convolutional(conv_mbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamplem0', downsample=True)
            return conv_lbbox + conv_mbbox

        if name == 'merge_sml':
            conv_lbbox = common.convolutional(conv_lbbox, filters_shape=(3, 3, self.in_channel, self.in_channel), trainable=True, name=name + 'convl1')
            conv_mbbox = common.convolutional(conv_mbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamplem0', downsample=True)
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamples0', downsample=True)
            conv_sbbox = common.convolutional(conv_sbbox, filters_shape=(3, 3, self.in_channel, self.in_channel),
                                              trainable=True, name=name+'_downsamples1', downsample=True)
            return conv_lbbox + conv_mbbox + conv_sbbox
            
            
            



            






    def vote_result(self, input_bbox_dict, input_labels):

            softmax_output = input_bbox_dict['lbbox_output']['output'] + input_bbox_dict['sbbox_output']['output'] + \
                                input_bbox_dict['mbbox_output']['output'] + input_bbox_dict['smbbox_output']['output'] + \
                                input_bbox_dict['slbbox_output']['output'] + input_bbox_dict['mlbbox_output']['output'] + \
                                input_bbox_dict['smlbbox_output']['output'] + input_bbox_dict['lbbox_resnet_output']['output'] + \
                                input_bbox_dict['sbbox_resnet_output']['output'] + input_bbox_dict['mbbox_resnet_output']['output'] + \
                                input_bbox_dict['smbbox_resnet_output']['output'] + input_bbox_dict['slbbox_resnet_output']['output'] + \
                                input_bbox_dict['mlbbox_resnet_output']['output'] + input_bbox_dict['sml_resnet_output']['output']
            
            cost = input_bbox_dict['lbbox_output']['cost'] + input_bbox_dict['mbbox_output']['cost'] + input_bbox_dict['sbbox_output']['cost'] + input_bbox_dict['smbbox_output']['cost'] + input_bbox_dict['slbbox_output']['cost']

            prediction_labels = tf.argmax(softmax_output, axis=1, name="output")
            read_labels = tf.argmax(input_labels, axis=1)
            correct_prediction = tf.equal(prediction_labels, read_labels)
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.int32))
            correct_times_in_batch = tf.reduce_sum(tf.cast(correct_prediction, tf.int32))
            fin_VGG_out = dict(
                cost=cost,
                correct_prediction=correct_prediction,
                correct_times_in_batch=correct_times_in_batch,
                prediction_labels=prediction_labels
            )
            
            softmax_output = input_bbox_dict['lbbox_output']['output'] + input_bbox_dict['sbbox_output']['output'] + \
                                input_bbox_dict['mbbox_output']['output'] + input_bbox_dict['smbbox_output']['output'] + \
                                input_bbox_dict['slbbox_output']['output'] + input_bbox_dict['mlbbox_output']['output'] + \
                                input_bbox_dict['smlbbox_output']['output']
                                
        

        
            

