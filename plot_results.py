import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
sampling =  ['reservoir-forgetting']
buffer_sizes = [100, 250, 500, 1000, 2500, 5000, 10000, 'inf']
sequences = [9, 10]
# sequences = [9]

# result_log_files = [f'./log/slam/{sampling}_{buffer_size}_c_k{sequence}' for ]

def find_line_num(text, path):
    file = open(path, 'r+')
    return [num for num,line in enumerate(file) if text in line]

def compound_results(sampling_methods, buffer_sizes, sequences):
    results = {}
    for sampling in sampling_methods:
        for buffer_size in buffer_sizes:
            log = f'{sampling}_{buffer_size}_c_k{sequences[0]}'
            path = Path(f'./log/slam/{log}') / 'log.txt'
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                trans_err_line_nums = find_line_num('Trans error (%):', path)
                rot_err_line_nums = find_line_num('Rot error (deg/100m):', path)
                abs_traj_rmse_line_nums = find_line_num('Abs traj RMSE (m):', path)
                rel_pose_err_m_line_nums = find_line_num('Rel pose error (m):', path)
                rel_pose_err_deg_line_nums = find_line_num('Rel pose err (deg):', path)

                trans_err = [float(lines[i].split()[-1]) for i in trans_err_line_nums]
                rot_err = [float(lines[i].split()[-1]) for i in rot_err_line_nums]
                abs_traj_rmse = [float(lines[i].split()[-1]) for i in abs_traj_rmse_line_nums]
                rel_pose_err_m = [float(lines[i].split()[-1]) for i in rel_pose_err_m_line_nums]
                rel_pose_err_deg = [float(lines[i].split()[-1]) for i in rel_pose_err_deg_line_nums]

                results[log] = {}
                results[log]['trans_err'] = trans_err
                results[log]['rot_err'] = rot_err
                results[log]['abs_traj_rmse'] = abs_traj_rmse
                results[log]['rel_pose_err_m'] = rel_pose_err_m
                results[log]['rel_pose_err_deg'] = rel_pose_err_deg
            for sequence in sequences[1:]:
                log = f'{log}_k{sequence}'
                path = Path(f'./log/slam/{log}') / 'log.txt'
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                    trans_err_line_nums = find_line_num('Trans error (%):', path)
                    rot_err_line_nums = find_line_num('Rot error (deg/100m):', path)
                    abs_traj_rmse_line_nums = find_line_num('Abs traj RMSE (m):', path)
                    rel_pose_err_m_line_nums = find_line_num('Rel pose error (m):', path)
                    rel_pose_err_deg_line_nums = find_line_num('Rel pose err (deg):', path)

                    trans_err = [float(lines[i].split()[-1]) for i in trans_err_line_nums]
                    rot_err = [float(lines[i].split()[-1]) for i in rot_err_line_nums]
                    abs_traj_rmse = [float(lines[i].split()[-1]) for i in abs_traj_rmse_line_nums]
                    rel_pose_err_m = [float(lines[i].split()[-1]) for i in rel_pose_err_m_line_nums]
                    rel_pose_err_deg = [float(lines[i].split()[-1]) for i in rel_pose_err_deg_line_nums]

                    results[log] = {}
                    results[log]['trans_err'] = trans_err
                    results[log]['rot_err'] = rot_err
                    results[log]['abs_traj_rmse'] = abs_traj_rmse
                    results[log]['rel_pose_err_m'] = rel_pose_err_m
                    results[log]['rel_pose_err_deg'] = rel_pose_err_deg
    return results

results = compound_results(sampling, buffer_sizes, sequences)

errors = ['trans_err', 'rot_err', 'abs_traj_rmse', 'rel_pose_err_m', 'rel_pose_err_deg']

fig, axes = plt.subplots(1,len(errors), figsize=(50, 10))
for i in range(len(errors)):
    mean_trans_errors = [np.mean(results[f'reservoir-forgetting_{buffer_size}_c_k9'][errors[i]]) for buffer_size in buffer_sizes[:-1]]
    mean_baseline_error = np.mean(results[f'reservoir-forgetting_inf_c_k9'][errors[i]])
    std_trans_errors = [np.std(results[f'reservoir-forgetting_{buffer_size}_c_k9'][errors[i]]) for buffer_size in buffer_sizes[:-1]]
    std_baseline_error = np.std(results[f'reservoir-forgetting_inf_c_k9'][errors[i]])
    axes[i].errorbar(buffer_sizes[:-1], mean_trans_errors, yerr=std_trans_errors, linestyle='None', marker='^', color='b', label='Reservoir-forgetting')
    axes[i].hlines(y=mean_baseline_error, xmin=0, xmax=buffer_sizes[-2], color='r', label='Infinite')
    axes[i].hlines(y=[mean_baseline_error-std_baseline_error, mean_baseline_error+std_baseline_error], xmin=0, xmax=buffer_sizes[-2], colors='red', linestyles='--', lw=2, label='Std Dev')

    axes[i].legend(loc='best')
    axes[i].set_title(f'{errors[i]} Reservoir-forgetting sampling c -> k9')
    axes[i].set_ylabel(errors[i])
    axes[i].set_xlabel('Buffer size')
    # axes[i].set_xscale('log')
    for j, txt in enumerate(buffer_sizes[:-1]):
        axes[i].annotate(txt, (buffer_sizes[:-1][j], mean_trans_errors[j]))
plt.savefig("log/reservoir-forgetting_results_c_k9.png")

fig, axes = plt.subplots(1,len(errors), figsize=(50, 10))
for i in range(len(errors)):
    mean_trans_errors = [np.mean(results[f'reservoir-forgetting_{buffer_size}_c_k9_k10'][errors[i]]) for buffer_size in buffer_sizes[:-1]]
    mean_baseline_error = np.mean(results[f'reservoir-forgetting_inf_c_k9_k10'][errors[i]])
    std_trans_errors = [np.std(results[f'reservoir-forgetting_{buffer_size}_c_k9_k10'][errors[i]]) for buffer_size in buffer_sizes[:-1]]
    std_baseline_error = np.std(results[f'reservoir-forgetting_inf_c_k9_k10'][errors[i]])
    axes[i].errorbar(buffer_sizes[:-1], mean_trans_errors, yerr=std_trans_errors, linestyle='None', marker='^', color='b', label='Reservoir-forgetting')
    axes[i].hlines(y=mean_baseline_error, xmin=0, xmax=buffer_sizes[-2], color='r', label='Infinite')
    axes[i].hlines(y=[mean_baseline_error-std_baseline_error, mean_baseline_error+std_baseline_error], xmin=0, xmax=buffer_sizes[-2], colors='red', linestyles='--', lw=2, label='Std Dev Inf')

    axes[i].legend(loc='best')
    axes[i].set_title(f'{errors[i]} Reservoir-forgetting sampling c -> k9 -> k10')
    axes[i].set_ylabel(errors[i])
    axes[i].set_xlabel('Buffer size')
    # axes[i].set_xscale('log')
    for j, txt in enumerate(buffer_sizes[:-1]):
        axes[i].annotate(txt, (buffer_sizes[:-1][j], mean_trans_errors[j]))
plt.savefig("log/reservoir-forgetting_results_c_k9_k10.png")
