import os
import pytest
import numpy as np
from paz.backend.camera import Camera
from paz.backend.image import load_image
from scipy.optimize import least_squares
from tensorflow.keras.utils import get_file
from paz.pipelines import EstimateHumanPose
from paz.processors import OptimizeHumanPose3D
from paz.datasets.human36m import args_to_joints3D


def get_optimized_posed3D(keypoints, camera_intrinsics):
    optimize_3D = OptimizeHumanPose3D(args_to_joints3D,
                                      least_squares, camera_intrinsics)
    _, optimized_poses3D = optimize_3D(keypoints['keypoints3D'],
                                       keypoints['keypoints2D'])
    return optimized_poses3D


def get_camera_intrinsics(image_height, image_width):
    camera = Camera()
    camera.intrinsics_from_HFOV(HFOV=70,
                                image_shape=[image_height, image_width])
    return camera.intrinsics


def get_poses(pipeline, image):
    keypoints = pipeline(image)
    return keypoints


@pytest.fixture
def model():
    pipeline = EstimateHumanPose()
    return pipeline


@pytest.fixture
def image_with_multiple_persons_A():
    URL = ('https://github.com/oarriaga/altamira-data/releases/download'
           '/v0.17/multiple_persons_posing.png')
    filename = os.path.basename(URL)
    fullpath = get_file(filename, URL, cache_subdir='paz/tests')
    image = load_image(fullpath)
    return image


@pytest.fixture
def image_with_single_person_B():
    URL = ('https://github.com/oarriaga/altamira-data/releases/download/'
           'v0.17/one_person_posing.png')
    filename = os.path.basename(URL)
    fullpath = get_file(filename, URL, cache_subdir='paz/tests')
    image = load_image(fullpath)
    return image


@pytest.fixture
def keypoints3D_multiple_persons():
    keypoints = np.array(
        [[0.00000000e+00, 0.00000000e+00, 0.00000000e+00, -1.14726820e+02,
          1.21343876e+01, -6.79812245e+01, -1.35863824e+02, 4.19467606e+02,
          9.37677967e+01, -2.14377161e+02, 8.06703618e+02, 2.89143238e+02,
          -1.15560633e+01, 7.42149725e+02, 1.66477287e+02, -1.18447102e+01,
          7.36763064e+02, 1.65182437e+02, 1.14726152e+02, -1.21343424e+01,
          6.79808542e+01, 1.27938000e+02, 4.13484511e+02, 1.91325905e+02,
          9.55896841e+01, 8.01181935e+02, 3.89558022e+02, -1.12642400e+01,
          7.48636864e+02, 1.66665977e+02, -1.14090840e+01, 7.36435064e+02,
          1.63713810e+02, 1.21660909e-03, -8.60110488e-02, -1.93000547e-02,
          4.52335487e+00, -2.49469926e+02, -6.15344365e+01, 2.27819061e+01,
          -4.84445853e+02, -1.72157425e+02, 5.55437990e+01, -5.64491792e+02,
          -2.90167339e+02, 2.12989218e+01, -6.77382407e+02, -2.97420008e+02,
          5.67537804e+00, -4.35088906e+02, -9.76974016e+01, 1.81741537e+02,
          -4.95856935e+02, -1.24252892e+02, 2.18840236e+02, -2.77173386e+02,
          -1.83449219e+02, -3.68658086e+01, -2.67203020e+02, -2.90879981e+02,
          1.26585821e+00, -1.20170579e+02, -2.82526049e+01, 1.57900698e+00,
          -1.51780249e+02, -3.52080548e+01, 8.84543990e-01, -1.07795356e+02,
          -2.56307189e+01, 8.84543990e-01, -1.07795356e+02, -2.56307189e+01,
          5.67537804e+00, -4.35088906e+02, -9.76974016e+01, -1.35515689e+02,
          -4.50778918e+02, -2.07550560e+02, -1.54306546e+02, -1.97581166e+02,
          -2.56477770e+02, 6.74229966e+01, -2.08812250e+02, -3.18276339e+02,
          8.70569018e-01, -1.68664569e+02, -3.73902498e+01, 1.39982513e+00,
          -2.00884252e+02, -4.47207875e+01, 5.24591118e-01, -1.65867774e+02,
          -3.68342864e+01, 5.24591118e-01, -1.65867774e+02, -3.68342864e+01]
         ])
    return np.reshape(keypoints, (-1, 32, 3))


@pytest.fixture
def keypoints2D_multiple_persons():
    return np.array(
        [297.97265625, 278.81640625, 270.41210938, 279.08398438, 265.59570312,
         384.50976562, 258.10351562, 480.30273438, 325.53320312, 278.54882812,
         330.34960938, 382.90429688, 334.63085938, 477.09179688, 297.97265625,
         212.45703125, 297.97265625, 146.09765625, 295.02929688, 86.96289062,
         340.51757812, 142.08398438, 348.54492188, 198.27539062, 283.79101562,
         195.06445312, 255.42773438, 150.11132812, 250.07617188, 211.65429688,
         308.40820312, 210.58398438])


@pytest.fixture
def keypoints3D_single_person():
    keypoints = np.array(
        [[0.00000000e+00, 0.00000000e+00, 0.00000000e+00, -1.01613821e+02,
          -1.57045238e+00, -7.83579210e+01, -1.28771002e+02, 3.03492329e+02,
          -1.30643458e+02, -2.01166429e+02, 6.75673518e+02, -1.05658365e+02,
          -1.15560633e+01, 7.42149725e+02, 1.66477287e+02, -1.18447102e+01,
          7.36763064e+02, 1.65182437e+02, 1.01614079e+02, 1.57052265e+00,
          7.83575426e+01, 7.93183401e+01, 3.39041783e+02, 1.92607564e+01,
          2.15506220e+01, 6.78448656e+02, 4.92480396e+01, -1.12642400e+01,
          7.48636864e+02, 1.66665977e+02, -1.14090840e+01, 7.36435064e+02,
          1.63713810e+02, 1.21660909e-03, -8.60110488e-02, -1.93000547e-02,
          -6.79559464e+00, -2.54716530e+02, -5.36947436e+01, 7.82148523e+00,
          -4.86618964e+02, -1.56544606e+02, 2.98269877e+01, -6.25791310e+02,
          -2.51405775e+02, 2.25821517e+01, -7.53364099e+02, -2.59546802e+02,
          5.67537804e+00, -4.35088906e+02, -9.76974016e+01, 2.02423399e+02,
          -5.18830395e+02, -8.32461342e+01, 2.62380803e+02, -2.59514591e+02,
          2.98386633e+01, 1.97672719e+02, -4.68176736e+01, -3.21776639e+01,
          1.26585821e+00, -1.20170579e+02, -2.82526049e+01, 1.57900698e+00,
          -1.51780249e+02, -3.52080548e+01, 8.84543990e-01, -1.07795356e+02,
          -2.56307189e+01, 8.84543990e-01, -1.07795356e+02, -2.56307189e+01,
          5.67537804e+00, -4.35088906e+02, -9.76974016e+01, -1.93475903e+02,
          -5.00181221e+02, -2.05483820e+02, -2.76693873e+02, -2.39491927e+02,
          -1.01124915e+02, -2.05551736e+02, 7.92245260e+00, -4.89243838e+01,
          8.70569018e-01, -1.68664569e+02, -3.73902498e+01, 1.39982513e+00,
          -2.00884252e+02, -4.47207875e+01, 5.24591118e-01, -1.65867774e+02,
          -3.68342864e+01, 5.24591118e-01, -1.65867774e+02, -3.68342864e+01]
         ])
    return np.reshape(keypoints, (-1, 32, 3))


@pytest.fixture
def keypoints2D_single_person():
    return np.array(
        [377.19726562, 627.07519531, 321.89941406, 625.61035156, 314.57519531,
         773.55957031, 282.34863281, 922.24121094, 432.49511719, 628.54003906,
         414.18457031, 780.15136719, 410.52246094, 919.31152344, 375.91552734,
         506.95800781, 374.63378906, 386.84082031, 382.69042969, 271.11816406,
         469.11621094, 387.57324219, 507.93457031, 515.01464844, 484.49707031,
         618.28613281, 280.15136719, 386.10839844, 239.13574219, 516.47949219,
         275.75683594, 625.61035156])


@pytest.fixture
def optimised_pose_single():
    return np.array(
        [[[379.14546419, 623.09036851, 332.95459673, 630.60799866,
           317.99031345, 782.736923, 285.33883186, 950.8225363, 374.28722941,
           889.32113006, 374.17730235, 887.63822093, 419.8848368,
           616.46005748, 412.56413148, 764.33694366, 387.87510047,
           898.19472804, 374.39768581, 891.72255546, 374.34153619,
           887.91676344, 379.1460497, 623.05540291, 376.28806425, 514.537561,
           383.57189444, 402.26947694, 396.19454712, 318.30218512,
           392.44936792, 247.79063978, 382.13603694, 431.22325513,
           472.39805414, 393.61980863, 488.88833657, 511.57973011,
           466.22190498, 605.74648303, 379.79649722, 573.23844459,
           379.96208683, 559.71646093, 379.61935833, 578.49694431,
           379.61935833, 578.49694431, 382.13603694, 431.22325513, 280.7106764,
           390.7309006, 250.46915996, 522.2382813, 287.61966409, 631.6406247,
           379.65800004, 552.36370612, 379.9216149, 538.35956766, 379.50306568,
           553.57488439, 379.50306568, 553.57488439
           ]]])


@pytest.fixture
def optimised_pose_multiple():
    return np.array(
        [[296.30768954, 284.34432606, 264.1639954, 288.1449868, 262.74598324,
          389.01706103, 249.39791995, 464.76570791, 294.41397126, 462.11493909,
          294.33613885, 460.95115235, 325.90476211, 280.84477042, 327.70875345,
          381.49605915, 318.65985703, 454.18147891, 294.48544345, 463.65740888,
          294.43174976, 461.0235712, 296.30789862, 284.3216423, 297.17762836,
          216.03695636, 301.92205887, 142.12640898, 312.10997308, 104.90989049,
          301.06415108, 67.48058475, 297.29655691, 162.369981, 347.63231942,
          142.99946747, 360.3828318, 202.94767912, 282.36161072, 200.53419182,
          296.48013542, 252.10753319, 296.5239252, 243.44934564, 296.3928208,
          255.47585153, 296.3928208, 255.47585153, 297.29655691, 162.369981,
          253.80519522, 149.09899402, 246.07008425, 224.21104975, 316.14243392,
          218.20720856, 296.3188961, 238.82741172, 296.41887751, 229.88578336,
          296.22840823, 239.59802759, 296.22840823, 239.59802759]]
    )


def test_simple_baselines_multiple_persons(image_with_multiple_persons_A,
                                           keypoints3D_multiple_persons,
                                           keypoints2D_multiple_persons,
                                           optimised_pose_multiple, model):
    keypoints = get_poses(model, image_with_multiple_persons_A)
    assert np.allclose(keypoints['keypoints2D'][0],
                       keypoints2D_multiple_persons)
    assert np.allclose(keypoints['keypoints3D'][0],
                       keypoints3D_multiple_persons)
    image_height, image_width = image_with_multiple_persons_A.shape[:2]
    camera_intrinsics = get_camera_intrinsics(image_height, image_width)
    optimized_poses3D = get_optimized_posed3D(keypoints, camera_intrinsics)
    assert np.allclose(optimized_poses3D[0], optimised_pose_multiple)


def test_simple_baselines_single_person(image_with_single_person_B,
                                        keypoints3D_single_person,
                                        keypoints2D_single_person,
                                        optimised_pose_single, model):
    keypoints = get_poses(model, image_with_single_person_B)
    assert np.allclose(keypoints['keypoints2D'], keypoints2D_single_person)
    assert np.allclose(keypoints['keypoints3D'], keypoints3D_single_person)
    image_height, image_width = image_with_single_person_B.shape[:2]
    camera_intrinsics = get_camera_intrinsics(image_height, image_width)
    optimized_poses3D = get_optimized_posed3D(keypoints, camera_intrinsics)
    assert np.allclose(optimized_poses3D, optimised_pose_single)
