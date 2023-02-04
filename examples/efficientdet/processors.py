import numpy as np
from paz.abstract import Processor
from paz.backend.image import resize_image
from paz.backend.image.draw import draw_rectangle
from paz import processors as pr
from draw import (compute_text_bounds, draw_opaque_box, make_box_transparent,
                  put_text)
from boxes import (nms_per_class, filter_boxes, BoxesToBoxes2D,
                   BoxesWithOneHotVectorsToBoxes2D, BoxesWithClassArgToBoxes2D)


class DivideStandardDeviationImage(Processor):
    """Divide channel-wise standard deviation to image.

    # Arguments
        standard_deviation: List of length 3, containing the
            channel-wise standard deviation.

    # Properties
        standard_deviation: List.

    # Methods
        call()
    """
    def __init__(self, standard_deviation):
        self.standard_deviation = standard_deviation
        super(DivideStandardDeviationImage, self).__init__()

    def call(self, image):
        return image / self.standard_deviation


class ScaledResize(Processor):
    """Resizes image by returning the scales to original image.

    # Arguments
        image_size: Int, desired size of the model input.

    # Properties
        image_size: Int.

    # Methods
        call()
    """
    def __init__(self, image_size):
        self.image_size = image_size
        super(ScaledResize, self).__init__()

    def call(self, image):
        """
        # Arguments
            image: Array, raw input image.
        """
        crop_offset_y = np.array(0)
        crop_offset_x = np.array(0)
        height = np.array(image.shape[0]).astype('float32')
        width = np.array(image.shape[1]).astype('float32')
        image_scale_y = np.array(self.image_size).astype('float32') / height
        image_scale_x = np.array(self.image_size).astype('float32') / width
        image_scale = np.minimum(image_scale_x, image_scale_y)
        scaled_height = (height * image_scale).astype('int32')
        scaled_width = (width * image_scale).astype('int32')
        scaled_image = resize_image(image, (scaled_width, scaled_height))
        scaled_image = scaled_image[
                       crop_offset_y: crop_offset_y + self.image_size,
                       crop_offset_x: crop_offset_x + self.image_size,
                       :]
        output_images = np.zeros((self.image_size,
                                  self.image_size,
                                  image.shape[2]))
        output_images[:scaled_image.shape[0],
                      :scaled_image.shape[1],
                      :scaled_image.shape[2]] = scaled_image
        image_scale = 1 / image_scale
        output_images = output_images[np.newaxis]
        return output_images, image_scale


class ScaleBox(Processor):
    """Scale box coordinates of the prediction.

    # Arguments
        scales: Array of shape `()`, value to scale boxes.

    # Properties
        scales: Int.

    # Methods
        call()
    """
    def __init__(self, scales):
        super(ScaleBox, self).__init__()
        self.scales = scales

    def call(self, boxes):
        boxes = scale_box(boxes, self.scales)
        return boxes


def scale_box(predictions, image_scales=None):
    """
    # Arguments
        predictions: Array of shape `(num_boxes, num_classes+N)`
            model predictions.
        image_scales: Array of shape `()`, scale value of boxes.

    # Returns
        predictions: Array of shape `(num_boxes, num_classes+N)`
            model predictions.
    """

    if image_scales is not None:
        boxes = predictions[:, :4]
        scales = image_scales[np.newaxis][np.newaxis]
        boxes = boxes * scales
        predictions = np.concatenate([boxes, predictions[:, 4:]], 1)
    return predictions


class NonMaximumSuppressionPerClass(Processor):
    """Applies non maximum suppression per class.

    # Arguments
        nms_thresh: Float between [0, 1].
        conf_thresh: Float between [0, 1].
    """
    def __init__(self, nms_thresh=.45, conf_thresh=0.01):
        self.nms_thresh = nms_thresh
        self.conf_thresh = conf_thresh
        super(NonMaximumSuppressionPerClass, self).__init__()

    def call(self, boxes):
        boxes = nms_per_class(boxes, self.nms_thresh, self.conf_thresh)
        return boxes


class FilterBoxes(Processor):
    """Filters boxes outputted from function ``detect`` as ``Box2D`` messages.

    # Arguments
        class_names: List of class names.
        conf_thresh: Float between [0, 1].
    """
    def __init__(self, class_names, conf_thresh=0.5):
        self.class_names = class_names
        self.conf_thresh = conf_thresh
        self.arg_to_class = dict(zip(
            list(range(len(self.class_names))), self.class_names))
        super(FilterBoxes, self).__init__()

    def call(self, boxes):
        boxes = filter_boxes(boxes, self.conf_thresh)
        return boxes


class ToBoxes2D(Processor):
    """Transforms boxes from dataset into `Boxes2D` messages.

    # Arguments
        class_names: List of class names ordered with respect to the class
            indices from the dataset ``boxes``.
    """
    def __init__(
            self, class_names=None, one_hot_encoded=False, box_type='Boxes',
            default_score=1.0):
        if class_names is not None:
            self.arg_to_class = dict(zip(range(len(class_names)), class_names))
        self.one_hot_encoded = one_hot_encoded
        self.box_type = box_type
        self.default_score = default_score
        super(ToBoxes2D, self).__init__()

    def call(self, boxes):
        if self.box_type == 'Boxes':
            boxes2D = BoxesToBoxes2D(boxes, self.default_score)
        elif self.box_type == 'BoxesWithOneHotVectors':
            boxes2D = BoxesWithOneHotVectorsToBoxes2D(boxes, self.arg_to_class)
        elif self.box_type == "BoxesWithClassArg":
            boxes2D = BoxesWithClassArgToBoxes2D(
                boxes, self.arg_to_class, self.default_score)
        else:
            raise ValueError('Invalid box type: ', self.box_type)
        return boxes2D


class DrawBoxes2D(pr.DrawBoxes2D):
    """Draws bounding boxes from Boxes2D messages.
    # Arguments
        class_names: List, class names.
        colors: List, color values.
        weighted: Bool, whether to weight bounding box color.
        scale: Float. Scale of text drawn.
        with_score: Bool, denoting if confidence be shown.
    # Methods
        compute_box_color()
        compute_text()
        get_text_box_parameters()
        call()
    """
    def __init__(
            self, class_names=None, colors=None,
            weighted=False, scale=0.7, with_score=True):
        super().__init__(
            class_names, colors, weighted, scale, with_score)

    def compute_box_color(self, box2D):
        class_name = box2D.class_name
        color = self.class_to_color[class_name]
        if self.weighted:
            color = [int(channel * box2D.score) for channel in color]
        return color

    def compute_text(self, box2D):
        class_name = box2D.class_name
        text = '{}'.format(class_name)
        if self.with_score:
            text = '{} :{}%'.format(class_name, round(box2D.score * 100))
        return text

    def get_text_box_parameters(self):
        thickness = 1
        offset_x = 2
        offset_y = 17
        color = (0, 0, 0)
        text_parameters = [thickness, offset_x, offset_y, color]
        box_start_offset = 2
        box_end_offset = 5
        box_color = (255, 174, 66)
        text_box_parameters = [box_start_offset, box_end_offset, box_color]
        return [text_box_parameters, text_parameters]

    def call(self, image, boxes2D):
        raw_image = image.copy()
        for box2D in boxes2D:
            x_min, y_min, x_max, y_max = box2D.coordinates.astype(np.int)
            color = self.compute_box_color(box2D)
            draw_opaque_box(image, (x_min, y_min), (x_max, y_max), color)
        image = make_box_transparent(raw_image, image)
        text_box_parameters, text_parameters = self.get_text_box_parameters()
        offset_start, offset_end, text_box_color = text_box_parameters
        text_thickness, offset_x, offset_y, text_color = text_parameters
        for box2D in boxes2D:
            x_min, y_min, x_max, y_max = box2D.coordinates.astype(np.int)
            color = self.compute_box_color(box2D)
            draw_rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)
            text = self.compute_text(box2D)
            text_size = compute_text_bounds(text, self.scale, text_thickness)
            (text_W, text_H), _ = text_size
            args = (image, (x_min + offset_start, y_min + offset_start),
                    (x_min + text_W + offset_end, y_min + text_H + offset_end),
                    text_box_color)
            draw_opaque_box(*args)
            args = (image, text, (x_min + offset_x, y_min + offset_y),
                    self.scale, text_color, text_thickness)
            put_text(*args)
        return image