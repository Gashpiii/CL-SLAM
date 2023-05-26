from pathlib import Path
import shutil

from torch.utils.data import DataLoader, Subset
from tqdm import tqdm

from datasets import Cityscapes
from slam.replay_buffer import ReplayBuffer

# ============================================================
def main(sampling, max_buffer_size, max_num_seen_examples):
    if max_buffer_size < 0:
        replay_buffer_path = Path(
            __file__).parent / f'log/cityscapes/replay_buffer_{sampling}_inf'
    else:
        replay_buffer_path = Path(
            __file__).parent / f'log/cityscapes/replay_buffer_{sampling}_{max_buffer_size}'
        
    if replay_buffer_path.exists(): # Clear buffer from previous experiment
        shutil.rmtree(replay_buffer_path)
    replay_buffer_path.mkdir(parents=True, exist_ok=True)
    replay_buffer = ReplayBuffer(replay_buffer_path, 'Cityscapes', sampling=sampling, max_buffer_size=max_buffer_size, max_num_seen_examples=max_num_seen_examples)

    # ============================================================

    dataset = Cityscapes(
        Path('/home/matiss/hdd/data/cityscapes/'),  # <-- ADJUST THIS
        'train',
        [-1, 0, 1],
        [0, 1, 2, 3],
        192,
        640,
        do_augmentation=False,
        views=('left', ),
    )
    dataloader = DataLoader(dataset, num_workers=8, batch_size=1, shuffle=False, drop_last=True)

    # ============================================================

    with tqdm(total=len(dataloader)) as pbar:
        for i, sample in enumerate(dataloader):
            replay_buffer.add(sample, dataset.get_item_filenames(i), verbose=True)
            pbar.update(1)
    replay_buffer.save_state()
