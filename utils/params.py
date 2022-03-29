import os

seq_len = 16
n_joints = 30


class MainConfig(object):
    def __init__(self):
        self.cam = "realsense"
        self.ar = "trx"
        self.cam_width = 640
        self.cam_height = 480
        self.window_size = seq_len
        self.just_text_port = 6050
        self.skeleton_scale = 2200.


class MetrabsTRTConfig(object):
    def __init__(self):
        self.yolo_engine_path = 'modules/hpe/modules/engines/yolo.engine'
        self.image_transformation_path = 'modules/hpe/modules/engines/image_transformation.engine'
        self.bbone_engine_path = 'modules/hpe/modules/engines/bbone.engine'
        self.head_weight_path = 'modules/hpe/modules/numpy/head_weights.npy'
        self.head_bias_path = 'modules/hpe/modules/numpy/head_bias.npy'
        self.expand_joints_path = 'assets/32_to_122.npy'
        self.skeleton_types_path = 'assets/skeleton_types.pkl'
        self.skeleton = 'smpl+head_30'
        self.yolo_thresh = 0.3
        self.nms_thresh = 0.7
        self.num_aug = 5


class RealSenseIntrinsics(object):
    def __init__(self):
        self.fx = 384.025146484375
        self.fy = 384.025146484375
        self.ppx = 319.09661865234375
        self.ppy = 237.75723266601562
        self.width = 640
        self.height = 480


class TRXConfig(object):
    def __init__(self):
        self.data_path = "D:/datasets/nturgbd_metrabs_2/" if 'Users' in os.getcwd() else "../nturgbd_metrabs_2/"
        self.n_workers = 2 if 'Users' in os.getcwd() else 12
        self.n_epochs = 10000
        self.log_every = 10 if 'Users' in os.getcwd() else 1000
        self.trt_path = 'modules/ar/modules/engines/FULL.engine'
        self.trans_linear_in_dim = 256
        self.trans_linear_out_dim = 128
        self.way = 5
        self.shot = 1
        self.query_per_class = 1
        self.trans_dropout = 0.
        self.seq_len = seq_len
        self.n_joints = n_joints
        self.num_gpus = 1
        self.temp_set = [2]
        self.device = 'cuda'


class FocusModelConfig:
    def __init__(self):
        self.name = 'resnet18'


class FaceDetectorConfig:
    def __init__(self):
        self.mode = 'mediapipe'
        self.mediapipe_max_num_faces = 1


class GazeEstimatorConfig:
    def __init__(self):
        self.camera_params = 'assets/camera_params.yaml'
        self.normalized_camera_params = 'assets/eth-xgaze.yaml'
        self.normalized_camera_distance = 0.6
        self.checkpoint = 'modules/focus/modules/raw/eth-xgaze_resnet18.pth'
        self.image_size = [224, 224]


class FocusConfig:
    def __init__(self):
        self.face_detector = FaceDetectorConfig()
        self.gaze_estimator = GazeEstimatorConfig()
        self.model = FocusModelConfig()
        self.mode = 'ETH-XGaze'
        self.device = 'cuda'
        self.area_thr = 0.03  # head bounding box must be over this value to be close
        self.close_thr = -0.95  # When close, z value over this thr is considered focus
        self.dist_thr = 0.3  # when distant, roll under this thr is considered focus
        self.foc_rot_thr = 0.7  # when close, roll above this thr is considered not focus
        self.patience = 16  # result is based on the majority of previous observations
