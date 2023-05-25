import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Slam:
    seed: int
    config_file: Path
    dataset_sequence: int
    adaptation: bool
    adaptation_epochs: int
    min_distance: float
    start_frame: int
    logging: bool
    do_loop_closures: bool
    keyframe_frequency: int
    lc_distance_poses: int

@dataclasses.dataclass
class ReplayBuffer:
    config_file: Path
    sampling: str
    max_buffer_size: int
    max_num_seen_examples: int
    load_path: Path