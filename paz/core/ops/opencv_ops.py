import colorsys
import random
import cv2

GREEN = (0, 255, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
LINE = cv2.LINE_AA
BGR2RGB = cv2.COLOR_BGR2RGB
RGB2BGR = cv2.COLOR_RGB2BGR
BGR2HSV = cv2.COLOR_BGR2HSV
RGB2HSV = cv2.COLOR_RGB2HSV
HSV2RGB = cv2.COLOR_HSV2RGB
HSV2BGR = cv2.COLOR_HSV2BGR
BGR2GRAY = cv2.COLOR_BGR2GRAY
IMREAD_COLOR = cv2.IMREAD_COLOR


class VideoPlayer(object):
    """Performs visualization inferences in a real-time video.

    # Properties
        image_size: List of two integers. Output size of the displayed image.
        pipeline: Function. Should take BGR image as input and it should
            output a dictionary with key 'image' containing a visualization
            of the inferences.
            Built-in pipelines can be found in paz/processing/pipelines.py
    # Methods
        start()

    # TODO:
        add method record()
    """

    def __init__(self, image_size, pipeline, camera=0):
        self.image_size = image_size
        self.pipeline = pipeline
        self.camera = camera

    def start(self):
        """ Opens camera and starts inference using the provided `pipeline`.
        """
        camera = cv2.VideoCapture(self.camera)
        while True:
            frame = camera.read()[1]
            if frame is None:
                print('Frame: None')
                continue

            results = self.pipeline(image=frame)
            image = cv2.resize(results['image'], tuple(self.image_size))
            cv2.imshow('webcam', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        camera.release()
        cv2.destroyAllWindows()


def cascade_classifier(path):
    """Cascade classifier with detectMultiScale() method for inference.
    # Arguments
        path: String. Path to default openCV XML format.
    """
    return cv2.CascadeClassifier(path)


def load_image(filepath, flags=cv2.IMREAD_COLOR):
    """Loads an image.
    # Arguments
        filepath: string with image path
        flags: Integers indicating flags about how to read image:
            1 or cv2.IMREAD_COLOR for BGR image.
            0 or cv2.IMREAD_GRAYSCALE for grayscale image.
           -1 or cv2.IMREAD_UNCHANGED for BGR with alpha-channel.
    # Returns
        Image as numpy array.
    """
    return cv2.imread(filepath, flags)


def resize_image(image, shape):
    """ Resizes image.
    # Arguments
        image: Numpy array.
        shape: List of two integer elements indicating new shape.
    """
    return cv2.resize(image, shape)


def save_image(filepath, image, *args):
    """Saves an image.
    # Arguments
        filepath: String with image path. It should include postfix e.g. .png
        image: Numpy array.
    """
    return cv2.imwrite(filepath, image, *args)


def convert_image(image, flag):
    """Converts image to a different color space
    # Arguments
        image: Numpy array
        flag: OpenCV color flag e.g. cv2.COLOR_BGR2RGB or BGR2RGB
    """
    return cv2.cvtColor(image, flag)


def show_image(image, name='image'):
    """ Shows image in an external window.
    # Arguments
        image: Numpy array
        name: String indicating the window name.
    """
    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def draw_circle(image, point, color=GREEN, radius=5):
    """ Draws a cirle in image.
    # Arguments
        image: Numpy array of shape [H, W, 3].
        point: List/tuple of length two indicating (y,x) openCV coordinates.
        color: List of length three indicating BGR color of point.
        radius: Integer indicating the radius of the point to be drawn.
    """
    cv2.circle(image, tuple(point), radius, (0, 0, 0), cv2.FILLED)
    inner_radius = int(.8 * radius)
    cv2.circle(image, tuple(point), inner_radius, tuple(color), cv2.FILLED)


def put_text(image, text, point, scale, color, thickness):
    """Draws text in image.
    # Arguments
        image: Numpy array.
        text: String. Text to be drawn.
        point: Tuple of coordinates indicating the top corner of the text.
        scale: Float. Scale of text.
        color: Tuple of integers. BGR color coordinates.
        thickness: Integer. Thickness of the lines used for drawing text.
    """
    return cv2.putText(image, text, point, FONT, scale, color, thickness, LINE)


def draw_line(image, point_A, point_B, color=GREEN, thickness=5):
    """ Draws a line in image from point_A to point_B.
    # Arguments
        image: Numpy array of shape [H, W, 3].
        point_A: List/tuple of length two indicating (y,x) openCV coordinates.
        point_B: List/tuple of length two indicating (y,x) openCV coordinates.
        color: List of length three indicating BGR color of point.
        thickness: Integer indicating the thickness of the line to be drawn.
    """
    cv2.line(image, tuple(point_A), tuple(point_B), tuple(color), thickness)


def draw_rectangle(image, corner_A, corner_B, color, thickness):
    """ Draws a filled rectangle from corner_A to corner_B.
    # Arguments
        image: Numpy array of shape [H, W, 3].
        corner_A: List/tuple of length two indicating (y,x) openCV coordinates.
        corner_B: List/tuple of length two indicating (y,x) openCV coordinates.
        color: List of length three indicating BGR color of point.
        thickness: Integer/openCV Flag. Thickness of rectangle line.
            or for filled use cv2.FILLED flag.
    """
    return cv2.rectangle(
        image, tuple(corner_A), tuple(corner_B), tuple(color), thickness)


def draw_dot(image, point, color=GREEN, radius=5, filled=True):
    """ Draws a dot (small rectangle) in image.
    # Arguments
        image: Numpy array of shape [H, W, 3].
        point: List/tuple of length two indicating (y,x) openCV coordinates.
        color: List of length three indicating BGR color of point.
        radius: Integer indicating the radius of the point to be drawn.
        filled: Boolean. If `True` rectangle is filled with `color`.
    """
    # drawing outer black rectangle
    point_A = (point[0] - radius, point[1] - radius)
    point_B = (point[0] + radius, point[1] + radius)
    draw_rectangle(image, tuple(point_A), tuple(point_B), (0, 0, 0), filled)

    # drawing innner rectangle with given `color`
    inner_radius = int(.8 * radius)
    point_A = (point[0] - inner_radius, point[1] - inner_radius)
    point_B = (point[0] + inner_radius, point[1] + inner_radius)
    draw_rectangle(image, tuple(point_A), tuple(point_B), color, filled)


def draw_cube(image, points, color=GREEN, thickness=2):
    """ Draws a cube in image.
    # Arguments
        image: Numpy array of shape [H, W, 3].
        points: List of length 8  having each element a list
            of length two indicating (y,x) openCV coordinates.
        color: List of length three indicating BGR color of point.
        thickness: Integer indicating the thickness of the line to be drawn.
    """
    # draw bottom
    draw_line(image, points[0], points[1], color, thickness)
    draw_line(image, points[1], points[2], color, thickness)
    draw_line(image, points[3], points[2], color, thickness)
    draw_line(image, points[3], points[0], color, thickness)

    # draw top
    draw_line(image, points[4], points[5], color, thickness)
    draw_line(image, points[6], points[5], color, thickness)
    draw_line(image, points[6], points[7], color, thickness)
    draw_line(image, points[4], points[7], color, thickness)

    # draw sides
    draw_line(image, points[0], points[4], color, thickness)
    draw_line(image, points[7], points[3], color, thickness)
    draw_line(image, points[5], points[1], color, thickness)
    draw_line(image, points[2], points[6], color, thickness)

    # draw X mark on top
    draw_line(image, points[4], points[6], color, thickness)
    draw_line(image, points[5], points[7], color, thickness)

    # draw dots
    # [draw_dot(image, point, color, point_radii) for point in points]


def warp_affine(image, matrix, fill_color=[0, 0, 0]):
    """ Transforms `image` using an affine `matrix` transformation.
    # Arguments
        image: Numpy array.
        matrix: Numpy array of shape (2,3) indicating affine transformation.
        fill_color: List/tuple representing BGR use for filling empty space.
    """
    height, width = image.shape[:2]
    return cv2.warpAffine(
        image, matrix, (width, height), borderValue=fill_color)


def draw_filled_polygon(image, vertices, color):
    """ Draws filled polygon
    # Arguments
        image: Numpy array.
        vertices: List of elements each having a list
            of length two indicating (y,x) openCV coordinates.
        color: Numpy array specifying BGR color of the polygon.
    """
    cv2.fillPoly(image, [vertices], color)


def median_blur(image, aperture):
    """ Blurs an image using the median filter.
    # Arguments
        image: Numpy array.
        aperture: Integer. Aperture linear size;
            it must be odd and greater than one.
    """
    return cv2.medianBlur(image, aperture)


def gaussian_blur(image, kernel_size):
    """ Blurs an image using the median filter.
    # Arguments
        image: Numpy array.
        kernel_size: List of two elements. Describes the gaussian kernel shape.
    """
    return cv2.GaussianBlur(image, kernel_size, 0)


def lincolor(num_colors, saturation=1, value=1, normalized=False):
    """Creates a list of RGB colors linearly sampled from HSV space with
    randomised Saturation and Value

    # Arguments
        num_colors: Integer.
        saturation: Float or `None`. If float indicates saturation.
            If `None` it samples a random value.
        value: Float or `None`. If float indicates value.
            If `None` it samples a random value.

    # Returns
        List, for which each element contains a list with RGB color

    # References
        [Original implementation](https://github.com/jutanke/cselect)
    """
    RGB_colors = []
    hues = [value / num_colors for value in range(0, num_colors)]
    for hue in hues:

        if saturation is None:
            saturation = random.uniform(0.6, 1)

        if value is None:
            value = random.uniform(0.5, 1)

        RGB_color = colorsys.hsv_to_rgb(hue, saturation, value)
        if not normalized:
            RGB_color = [int(color * 255) for color in RGB_color]
        RGB_colors.append(RGB_color)
    return RGB_colors
