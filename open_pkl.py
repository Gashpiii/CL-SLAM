import pickle
import numpy as np
from pathlib import Path
path = Path('/home/matiss/p/bep/CL-SLAM/log/slam/reservoir_100_c_k9/metrics.pkl')

with open(path, 'rb') as f:
    data = pickle.load(f)
    
print(data)