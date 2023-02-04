import numpy as np
from paz.abstract import Box2D
from paz.backend.boxes import apply_non_max_suppression


def nms_per_class(box_data, nms_thresh=.45, conf_thresh=0.01, top_k=200):
    """Applies non-maximum-suppression per class.
    # Arguments
        box_data: Numpy array of shape `(num_prior_boxes, 4 + num_classes)`.
        nsm_thresh: Float. Non-maximum suppression threshold.
        conf_thresh: Float. Filter scores with a lower confidence value before
            performing non-maximum supression.
        top_k: Integer. Maximum number of boxes per class outputted by nms.

    Returns
        Numpy array of shape `(num_classes, top_k, 5)`.
    """
    decoded_boxes, class_predictions = box_data[:, :4], box_data[:, 4:]
    num_classes = class_predictions.shape[1]
    output = np.array([], dtype=float).reshape(0, box_data.shape[1])
    for class_arg in range(num_classes):
        mask = class_predictions[:, class_arg] >= conf_thresh
        scores = class_predictions[:, class_arg][mask]
        if len(scores) == 0:
            continue
        boxes = decoded_boxes[mask]
        indices, count = apply_non_max_suppression(
            boxes, scores, nms_thresh, top_k)
        scores = np.expand_dims(scores, -1)
        selected_indices = indices[:count]
        classes = class_predictions[mask]
        selections = np.concatenate(
            (boxes[selected_indices],
             classes[selected_indices]), axis=1)
        output = np.concatenate((output, selections))
    return output


def filter_boxes(boxes, conf_thresh):
    max_class_score = np.max(boxes[:, 4:], axis=1)
    confidence_mask = max_class_score >= conf_thresh
    confident_class_detections = boxes[confidence_mask]
    return confident_class_detections


def BoxesToBoxes2D(boxes, default_score):
    boxes2D = []
    for box in boxes:
        boxes2D.append(Box2D(box[:4], default_score, None))
    return boxes2D


def BoxesWithOneHotVectorsToBoxes2D(boxes, arg_to_class):
    boxes2D = []
    for box in boxes:
        score = np.max(box[4:])
        class_arg = np.argmax(box[4:])
        class_name = arg_to_class[class_arg]
        boxes2D.append(Box2D(box[:4], score, class_name))
    return boxes2D


def BoxesWithClassArgToBoxes2D(boxes, arg_to_class, default_score):
    boxes2D = []
    for box in boxes:
        class_name = arg_to_class[box[-1]]
        boxes2D.append(Box2D(box[:4], default_score, class_name))
    return boxes2D