import numpy as np
from tqdm import tqdm

from config.config_parser import ConfigParser
from slam import Slam
from slam.utils import calc_error, set_random_seed

def main():
    # ============================================================
    config = ConfigParser('./config/config_adapt.yaml')
    print(config)
    set_random_seed(config.slam.seed)
    # ============================================================
    slam = Slam(config)

    with tqdm(desc='SLAM', total=len(slam)) as pbar:
        while slam.current_step < len(slam):
            losses = slam.step()
            pbar.set_postfix(depth=f'{losses["depth_loss"]:.5f}', velo=f'{losses["velocity_loss"]:.5f}')
            pbar.update(1)
            if slam.predictor.nan_loss_error:
                print("ENCOUNTERED NAN LOSS... RETRYING")
                break
    if not slam.predictor.nan_loss_error:
        if slam.do_adaptation:
            slam.save_model()
        if slam.logging:
            slam.save_metrics()
            slam.plot_metrics()
            slam.plot_trajectory()
        error_log = calc_error(slam.pose_graph.get_all_poses(), slam.gt_pose_graph.get_all_poses(), seed=config.slam.seed)
        print(error_log)

        with open(config.depth_pose.log_path / 'log.txt', 'a', encoding='utf-8') as file:
            file.write(error_log)
    else:
        main()
# print(f'Rel pose error (m):     {np.array(slam.rel_trans_error).mean():.4f}')
# print(f'Rel pose err (deg):     {np.array(slam.rel_rot_error).mean() * 180 / np.pi:.4f}')
