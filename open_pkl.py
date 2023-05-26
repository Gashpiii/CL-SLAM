import pickle
import numpy as np
from pathlib import Path
# path = Path('/home/matiss/p/bep/CL-SLAM/log/slam/reservoir_100_c_k9/metrics.pkl')
path = Path('/home/matiss/p/bep/CL-SLAM/log/cityscapes/replay_buffer_reservoir_inf/buffer_state.pkl')

with open(path, 'rb') as f:
    data = pickle.load(f)
    
print(data.keys())
print(data['num_seen_examples'].keys())