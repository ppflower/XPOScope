import numpy as np
from dynamicExerciser.picLabel.core import utils as utils
from dynamicExerciser.picLabel.core.config import cfg
import matplotlib.pyplot as plt

classes            = utils.read_class_names(cfg.YOLO.CLASSES)
num_classes        = len(classes)
batchsize          = cfg.TEST.BATCH_SIZE
min_overlap        = 0.5
score_threshold    = cfg.TEST.SCORE_THRESHOLD
iou_threshold      = cfg.TEST.IOU_THRESHOLD
inputsize          = cfg.TEST.INPUT_SIZE
def get_ground_truth(annotation):
    annotation = annotation.strip().split('$&')
    size = (int(annotation[2]), int(annotation[3]))
    groud_box = []
    # size = (int(annotation[2]), int(annotation[3]))
    # IPython.embed()
    bbox_data_gt = np.array([list(map(int, box.split(','))) for box in annotation[4:]])
    # bbox_data_gt = annotation
    if len(bbox_data_gt) == 0:
        bboxes_gt=[]
        classes_gt=[]
    else:
        bboxes_gt, classes_gt = bbox_data_gt[:, :4], bbox_data_gt[:, 4]
    num_bbox_gt = len(bboxes_gt)
    for i in range(num_bbox_gt):
        class_name = classes[classes_gt[i]]
        xmin, ymin, xmax, ymax = list(map(int, bboxes_gt[i]))
        groud_box.append([class_name, 0, xmin, ymin, xmax, ymax])
    return groud_box, size


def voc_ap(rec, prec):
    """
    --- Official matlab code VOC2012---
    mrec=[0 ; rec ; 1];
    mpre=[0 ; prec ; 0];
    for i=numel(mpre)-1:-1:1
        mpre(i)=max(mpre(i),mpre(i+1));
    end
    i=find(mrec(2:end)~=mrec(1:end-1))+1;
    ap=sum((mrec(i)-mrec(i-1)).*mpre(i));
    """
    rec.insert(0, 0.0) # insert 0.0 at begining of list
    rec.append_children_node(1.0) # insert 1.0 at end of list
    mrec = rec[:]
    prec.insert(0, 0.0) # insert 0.0 at begining of list
    prec.append_children_node(0.0) # insert 0.0 at end of list
    mpre = prec[:]
    """
    This part makes the precision monotonically decreasing
    (goes from the end to the beginning)
    matlab:  for i=numel(mpre)-1:-1:1
                mpre(i)=max(mpre(i),mpre(i+1));
    """
    # matlab indexes start in 1 but python in 0, so I have to do:
    #   range(start=(len(mpre) - 2), end=0, step=-1)
    # also the python function range excludes the end, resulting in:
    #   range(start=(len(mpre) - 2), end=-1, step=-1)
    for i in range(len(mpre)-2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i+1])
    """
    This part creates a list of indexes where the recall changes
    matlab:  i=find(mrec(2:end)~=mrec(1:end-1))+1;
    """
    i_list = []
    for i in range(1, len(mrec)):
        if mrec[i] != mrec[i-1]:
            i_list.append(i) # if it was matlab would be i + 1
    """
    The Average Precision (AP) is the area under the curve
    (numerical integration)
    matlab: ap=sum((mrec(i)-mrec(i-1)).*mpre(i));
    """
    ap = 0.0
    for i in i_list:
        ap += ((mrec[i]-mrec[i-1])*mpre[i])
    return ap, mrec, mpre



def compute_MAP(groud_truth, pred_sbbox, pred_mbbox, pred_lbbox):
    
    sum_AP = 0.0
    for num in range(batchsize):
        groud_box, size = get_ground_truth(groud_truth[num])
        org_w, org_h = size[0], size[1]
        pred_bbox = np.concatenate([np.reshape(pred_sbbox[num], (-1, 5 + num_classes)),
                                    np.reshape(pred_mbbox[num], (-1, 5 + num_classes)),
                                    np.reshape(pred_lbbox[num], (-1, 5 + num_classes))],  axis=0)
        bboxes = utils.postprocess_boxes(pred_bbox, (org_h, org_w), 512, score_threshold) # 返回原本图像大小的框并且去掉分数小于阈值的框
        bboxes = utils.nms(bboxes, iou_threshold)  #nms抑制的处理
        bbox_predict = []
        for bbox in bboxes:
            coor = np.array(bbox[:4], dtype=np.int32)
            score = bbox[4]
            class_ind = int(bbox[5])
            class_name = classes[class_ind]
            score = '%.4f' % score
            xmin, ymin, xmax, ymax = list(map(int, coor))
            bbox_predict.append([class_name, score, xmin, ymin, xmax, ymax])

        bbox_predict.sort(key=lambda x:float(x[1]), reverse=True)
        tp = [0] * len(bbox_predict)
        fp = [0] * len(bbox_predict)

        
        for idx, bb in enumerate(bbox_predict):
            ovmax = -1
            gt_match = -1
            for bbgt in groud_box:
                if bb[0] == bbgt[0]:
                    bi = [max(bb[2],bbgt[2]), max(bb[3],bbgt[3]), min(bb[4],bbgt[4]), min(bb[5],bbgt[5])]
                    iw = bi[2] - bi[0] + 1
                    ih = bi[3] - bi[1] + 1
                    if iw > 0 and ih > 0:
                        ua = (bb[4] - bb[2] + 1) * (bb[5] - bb[3] + 1) + (bbgt[4] - bbgt[2]
                            + 1) * (bbgt[5] - bbgt[3] + 1) - iw * ih
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
        ap, mrec, mprec = voc_ap(rec, prec)
        sum_AP += ap
    mAP = sum_AP / batchsize
    return mAP


def draw_MAP(map_list):
    map_list = [0.56, 0.54, 0.56, 0.54, 0.51, 0.56, 0.51, 0.50, 0.50]
    plt.plot(np.arange(len(map_list)), map_list)
    plt.ylabel('MAP')
    plt.xlabel('epochs')
    plt.savefig('./mAP/results/MAP.jpg')



