import pickle
import numpy as np
from pathlib import Path
# state_paths = [f'./log/cityscapes/replay_buffer_most-recent_{buffer_size}/buffer_state.pkl' for buffer_size in [100, 250, 500, 1000, 2500, 5000, 10000]]
# state_paths = [f'./log/cityscapes/replay_buffer_reservoir_{buffer_size}/buffer_state.pkl' for buffer_size in ['inf']]
state_paths = [f'./log/slam/most-recent_2500_c_k9/replay_buffer/buffer_state.pkl']



for state_path in state_paths:
    with open(state_path, 'rb') as f:
        data = pickle.load(f)
        filenames = data['filenames']
    # filenames_replace = [Path('/home/matiss/p/bep/CL-SLAM/')/Path(state_path).parent/filename.name for filename in filenames]
    # print(filenames_replace)
    # print(filenames)
    # if type(filenames) == list and filenames != filenames_replace:
    #     filenames = filenames
    # if type(filenames) == dict:
    #     filenames = filenames['cityscapes']
    # filenames_replace = [Path('/home/matiss/p/bep/CL-SLAM/')/Path(state_path).parent/filename.name for filename in filenames]

    num_seen_examples = {'cityscapes': 83300, 'kitti': 1582}
    # # # print(filenames)
    data = {'filenames': filenames, 'num_seen_examples': num_seen_examples}
    # # # print(data.keys())

    with open(state_path, 'wb') as f:
        pickle.dump(data, f)

    with open(state_path, 'rb') as f:
        read_data = pickle.load(f)
    print(read_data['num_seen_examples'])

# with open(state_paths[0], 'rb') as f:
#     data = pickle.load(f)
#     filenames = data['filenames']
#     faiss_index = data['faiss_index']
#     dataset_types = data['buffer_dataset_types']
#     num_seen_examples = data['num_seen_examples']
