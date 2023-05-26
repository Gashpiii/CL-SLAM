import pickle
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import os

import torch
from PIL import Image
from torch import Tensor
from torch.utils.data import Dataset as TorchDataset
from torchvision import transforms

from datasets.utils import get_random_color_jitter


class ReplayBuffer(TorchDataset):
    def __init__(
        self,
        storage_dir: Path,
        dataset_type: str,
        state_path: Optional[Path] = None,
        height: int = 0,
        width: int = 0,
        scales: List[int] = None,
        frames: List[int] = None,
        num_workers: int = 1,
        do_augmentation: bool = False,
        sampling: str = 'reservoir',
        max_buffer_size: int = 100,
        max_num_seen_examples: int = 10000

    ):
        # storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir = storage_dir
        self.dataset_type = dataset_type.lower()
        self.num_workers = num_workers
        self.do_augmentation = do_augmentation
        self.num_seen_examples = {self.dataset_type: 0}

        # Restrict size of the replay buffer
        self.NUMBER_SAMPLES_PER_ENVIRONMENT = 100
        self.valid_indices = {}

        self.buffer_filenames = {}
        self.online_filenames = []
        
        self.num_seen_examples = {self.dataset_type: 1}

        if state_path is not None:
            self.load_state(state_path)

        if sum(self.num_seen_examples.values()) > max_num_seen_examples:
            self.max_num_seen_examples = max_num_seen_examples
        else:
            self.max_num_seen_examples = sum(self.num_seen_examples.values())
            
        # Precompute the resize functions for each scale relative to the previous scale
        # If scales is None, the size of the raw data will be used
        self.scales = scales
        self.frames = frames
        self.resize = {}
        if self.scales is not None:
            for s in self.scales:
                exp_scale = 2**s
                self.resize[s] = transforms.Resize(
                    (height // exp_scale, width // exp_scale),
                    interpolation=transforms.InterpolationMode.LANCZOS)

        self.sampling = sampling
        self.buffer_size = max_buffer_size
        if max_buffer_size < 0:
            print('Infinite buffer size')
            self.buffer_size = np.inf

    def add(self, sample: Dict[str, Any], sample_filenames: Dict[str, Any], verbose: bool = True):
        add_sample = False
        remove_sample = None
        replace = False # Add at same index where file was removed

        if self.sampling == 'reservoir':
            index = sample['index'].item()
            assert index == sample_filenames['index']
            index = self.num_seen_examples[self.dataset_type]

            if sum(self.num_seen_examples.values()) <= self.buffer_size:
                add_sample = True
            else:
                remove_index = np.random.randint(0, sum(self.num_seen_examples.values()) + 1)
                if remove_index < self.buffer_size:
                    add_sample = True
                    replace = True
                    # remove_sample = int(self.online_filenames[remove_index].name[-9:-4])
                    remove_sample = self.online_filenames[remove_index].name

        elif self.sampling == 'most-recent':
            index = sample['index'].item()
            assert index == sample_filenames['index']
            index = self.num_seen_examples[self.dataset_type]

            add_sample = True
            
            if sum(self.num_seen_examples.values()) > self.buffer_size:
                remove_index = 0
                remove_sample = self.online_filenames[remove_index].name
                
        elif self.sampling == 'reservoir-forgetting':
            index = sample['index'].item()
            assert index == sample_filenames['index']
            index = self.num_seen_examples[self.dataset_type]

            if self.max_num_seen_examples <= self.buffer_size:
                add_sample = True
            else:
                remove_index = np.random.randint(0, self.max_num_seen_examples + 1)
                if remove_index < self.buffer_size:
                    add_sample = True
                    replace = True
                    # remove_sample = int(self.online_filenames[remove_index].name[-9:-4])
                    remove_sample = self.online_filenames[remove_index].name
            self.max_num_seen_examples += 1

        if add_sample:
            filename = self.storage_dir / f'{self.dataset_type}_{index:>05}.pkl'
            data = {
                key: value
                for key, value in sample.items() if 'index' in key or 'camera_matrix' in key
                or 'inv_camera_matrix' in key or 'relative_distance' in key
            }
            data['rgb', -1] = sample_filenames['images'][0]
            data['rgb', 0] = sample_filenames['images'][1]
            data['rgb', 1] = sample_filenames['images'][2]
            with open(filename, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            if replace:
                self.online_filenames[remove_index] = filename
            else:
                self.online_filenames.append(filename)
            if verbose:
                print(f'Added sample {self.dataset_type}_{index:>05}.pkl to the replay buffer')
            
        if remove_sample is not None:
            if not replace:
                for filename in self.online_filenames:
                    if remove_sample == filename.name:
                        os.remove(filename)
                        self.online_filenames.remove(filename)
                        break
            else:
                os.remove(self.storage_dir / remove_sample)
            if verbose:
                print(f'Removed sample {remove_sample} to the replay buffer')
        self.num_seen_examples[self.dataset_type] += 1

    def get(self) -> Dict[str, Any]:
        return_data = {}

        index = random.randint(0, len(self.online_filenames) - 1)
        # index = random.sample(self.valid_indices[dataset], 1)[0]
        filename = self.online_filenames[index]
        data = self._get(filename)
        return_data = data
        # if not return_data:
        #     return_data = data
        # else:
        #     for key in return_data:
        #         return_data[key] = torch.cat([return_data[key], data[key]])
        return return_data

    def save_state(self):
        filename = self.storage_dir / 'buffer_state.pkl'
        data = {'filenames': self.online_filenames, 'num_seen_examples': self.num_seen_examples}
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        print(f'Saved reply buffer state to: {filename}')
        for key, value in self.buffer_filenames.items():
            print(f'{key + ":":<12} {len(value):>5}')

    def load_state(self, state_path: Path):
        with open(state_path, 'rb') as f:
            data = pickle.load(f)
            self.online_filenames = data['filenames']
            self.num_seen_examples = data['num_seen_examples']
            if self.dataset_type not in self.num_seen_examples.keys():
                self.num_seen_examples[self.dataset_type] = 0
            self.num_seen_examples[self.dataset_type] += 1
        print(f'Load replay buffer state from: {state_path}')
        for key, value in self.buffer_filenames.items():
            print(f'{key + ":":<12} {len(value):>5}')

        # for key, value in self.buffer_filenames.items():
        #     center_sequences = sorted(random.sample(range(len(value)),
        #                                             self.NUMBER_SAMPLES_PER_ENVIRONMENT))
        #     assert center_sequences[0] >= 1 and center_sequences[-1] <= len(value)-2
        #     self.valid_indices[key] = center_sequences
            # print(f'{key + ":":<12} {len(center_sequences):>5}')

    def __getitem__(self, index: int) -> Dict[Any, Tensor]:
        return self.get()

    def __len__(self):
        return 1000000  # Fixed number as the sampling is handled in the get() function

    def _get(self, filename, include_batch=True):
        if self.do_augmentation:
            color_augmentation = get_random_color_jitter((0.8, 1.2), (0.8, 1.2), (0.8, 1.2),
                                                         (-.1, .1))

        with open(filename, 'rb') as f:
            data = pickle.load(f)
        for frame in self.frames:
            rgb = Image.open(data['rgb', frame]).convert('RGB')
            rgb = self.resize[0](rgb)
            data['rgb', frame, 0] = rgb
            for scale in self.scales:
                if scale == 0:
                    continue
                data['rgb', frame, scale] = self.resize[scale](data['rgb', frame, scale - 1])
            for scale in self.scales:
                data['rgb', frame, scale] = transforms.ToTensor()(data['rgb', frame, scale])
                if include_batch:
                    data['rgb', frame, scale] = data['rgb', frame, scale].unsqueeze(0)
                if self.do_augmentation:
                    data['rgb_aug', frame, scale] = color_augmentation(data['rgb', frame, scale])
                else:
                    data['rgb_aug', frame, scale] = data['rgb', frame, scale]
            del data['rgb', frame]  # Removes the filename string
        if not include_batch:
            for key in data:
                if not ('rgb' in key or 'rgb_aug' in key):
                    data[key] = data[key].squeeze(0)
        return data
