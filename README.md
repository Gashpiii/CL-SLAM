# Continual SLAM With Finite Replay Buffer Size
Explored what impact having a finite replay buffer size would have on [CL-SLAM](https://arxiv.org/abs/2203.01578) performance.

[paper](https://github.com/Gashpiii/CL-SLAM/blob/tue_thesis/continual_slam_with_finite_replay_buffer_size.pdf)

# 🏗 Setup

Clone repository: `git clone --recurse-submodules https://github.com/Gashpiii/CL-SLAM/tree/tue_thesis`

## ⚙️ Installation
- Create conda environment: `conda create --name continual_slam python=3.8`
- Activate conda environment: `conda activate continual_slam`
- Install dependencies: `pip install -r requirements.txt`
- For smooth development, install git hook scripts: `pre-commit install`

## 🔄 Install [g2opy](https://github.com/uoip/g2opy)
g2o is used for pose graph optimization.
- Apply fixes for Eigen version >= 3.3.5: `./third_party/fix_g2opy.py`
- Install C++ requirements:
  - `conda install cmake`
  - `conda install -c conda-forge eigen`
  - `conda install -c conda-forge suitesparse`
- Install g2opy:
```
cd third_party/g2opy
mkdir build
cd build
cmake -DPYBIND11_PYTHON_VERSION=3.8 ..
make -j8        |NOTE: reduce number if running out of memory
cd ..
|NOTE: remove any .so file which is not for Python 3.8
python setup.py install  |NOTE: Ensure that the conda environment is active
```

## 💾 Data preparation
To re-train or run the experiments from our paper, please download and pre-process the respective datasets.

### Cityscapes
Download the following files from https://www.cityscapes-dataset.com/downloads/:
- `leftImg8bit_sequence_trainvaltest.zip` (324GB)
- `timestamp_sequence.zip` (40MB)
- `vehicle_sequence.zip` (56MB)
- `disparity_sequence_trainvaltest.zip` (106GB) (optionally, used for computing the depth error)

### KITTI
Download the KITTI Odometry data from http://www.cvlibs.net/datasets/kitti/eval_odometry.php:
- `odometry data set (color, 65 GB)`
- `odometry ground truth poses (4 MB)`

Download the KITTI raw data from http://www.cvlibs.net/datasets/kitti/raw_data.php for the runs specified in [`datasets/kitti.py`](datasets/kitti.py) (search for `KITTI_RAW_SEQ_MAPPING`).
- `[synced+rectified data]`

Download the ground truth depth from http://www.cvlibs.net/datasets/kitti/eval_depth_all.php (optionally, used for computing the depth error).
- `annotated depth maps data set (14GB)`

Extract the raw data matching the odometry dataset. Note that sequence 03 is excluded as no IMU data (KITTI raw) has been released.
```python
python datasets/kitti.py <RAW_PATH> <ODOMETRY_PATH> --oxts
python datasets/kitti.py <GT_DEPTH_PATH> <ODOMETRY_PATH> --depth
```


# 🏃 Running the Code

## 🏋 Pre-training
The original authors pre-trained CL-SLAM on the Cityscapes Dataset.
You can either download the resulting weights, where they masked potentially dynamic objects, or pre-train the DepthNet and PoseNet by yourself by running the code.
**Note** that you have to adjust the `dataset_path` in [`config/config_pretrain.yaml`](config/config_pretrain.yaml).
```python
python main_pretrain.py
```
Model weights: http://continual-slam.cs.uni-freiburg.de/static/models/cityscapes_masks_pretrain.zip (Please unzip the file after download.)


## 🗺️ Adaptation with CL-SLAM
For adaptation, KITTI Odometry Dataset is used.
The experiments in the paper are conducted on the KITTI sequences 09 and 10.
<br>In order to fill the replay buffer with the pre-training data, please run the following script after having adjusted the paths in the file.
This can take some time.
```python
python make_cityscapes_buffer.py
```
In the configuration file [`config/config_adapt.yaml`](config/config_adapt.yaml), please adjust the following parameters:
- `Dataset.dataset` --> Set either `Kitti` or `RobotCar`
- `Dataset.dataset_path` --> Set the path to the data
- `DepthPosePrediction.load_weights_folder` --> Should be the path to the weights from pre-training or the previous adaptation
- `ReplayBuffer.sampling` --> Set to either `most-recent`, `reservoir` or `reservoir-forgetting`  
- `ReplayBuffer.max_buffer_size` --> Set to a natural number which would indicate the maximum number of samples the replay buffer can store
- `ReplayBuffer.max_num_seen_examples` --> Set to a natural number if `reservoir-forgetting` is used as the sampling method
- `ReplayBuffer.load_path` --> Should be the path to the pre-taining data filled replay buffer or the replay buffer from the previous adaptation
- `Slam.dataset_sequence` --> Set the KITTI sequence
- `Slam.logging` --> If this is set to true, make sure to enable dataloaders in the [`slam/slam.py`](slam/slam.py) have `with_depths` argument set to `True`, also make sure that you have `gt_depth` in your dataset folder

Then run:
```python
python main_adapt.py
```


## 🙏 Acknowledgment

This is part of a TU/e Bachelor Thesis. Under the supervision of Hemang Chawla.
