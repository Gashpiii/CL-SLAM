import main_adapt
sampling_methods = ['reservoir-forgetting', 'most-recent', 'reservoir']
# sampling = 'reservoir'
# buffer_sizes = [2500, 5000, 10000]
# buffer_sizes = [1000, 2500, 5000, 10000]
buffer_sizes = [100, 250, 500, 1000, 2500, 5000, 10000]
sequences = [9, 10] # note: first sequence is actually c since model is pre-trained on that
# buffer_sizes = [100]
seeds = [4, 42, 218]
max_num_seen_examples = 10000
def find_line_num(text, path):
    file = open(path, 'r+')
    return [num for num,line in enumerate(file) if text in line][0]

def modify_config(path, seed, log_path, load_weights_folder, sampling, max_buffer_size
                  , max_num_seen_examples, load_path, dataset_sequence, adaptation):
    config = open(path, 'r+')
    lines = config.readlines()
    config.seek(0)

    lines[find_line_num('  seed', path)] = f'  seed: {seed}\n'    
    lines[find_line_num('  log_path', path)] = f'  log_path: {log_path}\n'    
    lines[find_line_num('  load_weights_folder', path)] = f'  load_weights_folder: {load_weights_folder}\n'
    lines[find_line_num('  sampling', path)] = f'  sampling: {sampling}\n'
    lines[find_line_num('  max_buffer_size', path)] = f'  max_buffer_size: {max_buffer_size}\n'
    lines[find_line_num('  max_num_seen_examples', path)] = f'  max_num_seen_examples: {max_num_seen_examples}\n'
    lines[find_line_num('  load_path', path)] = f'  load_path: {load_path}\n'
    lines[find_line_num('  dataset_sequence', path)] = f'  dataset_sequence: {dataset_sequence}\n'
    lines[find_line_num('  adaptation', path)] = f'  adaptation: {adaptation}\n'
    
    config.writelines(lines)
    config.truncate()
    config.close()

def run_experiments(seeds, sampling_methods, buffer_sizes, sequences, max_num_seen_examples):
    for sampling in sampling_methods:
        for seed in seeds:
            for buffer_size in buffer_sizes:
                if buffer_size < 0 and sampling:
                    log_path = f'./log/slam/{sampling}_inf_c_k{sequences[0]}'
                    load_path = f'./log/cityscapes/replay_buffer_{sampling}_inf'

                else:
                    log_path = f'./log/slam/{sampling}_{buffer_size}_c_k{sequences[0]}'
                    load_path = f'./log/cityscapes/replay_buffer_{sampling}_{buffer_size}'
                
                path = './config/config_adapt.yaml'
                seed = seed
                load_weights_folder = './log/cityscapes/models/weights_025/'
                sampling = sampling
                max_buffer_size = buffer_size # set to negative if infinite
                max_num_seen_examples = max_num_seen_examples
                dataset_sequence = sequences[0]
                adaptation = 'True'

                modify_config(path, seed, log_path, load_weights_folder, sampling, max_buffer_size
                    , max_num_seen_examples, load_path, dataset_sequence, adaptation)
                main_adapt.main()
                for sequence in sequences[1:]:
                    load_weights_folder = f'{log_path}/models/weights_025'
                    load_path = f'{log_path}/replay_buffer'
                    log_path = f'{log_path}_k{sequence}'
                    dataset_sequence = sequence

                    modify_config(path, seed, log_path, load_weights_folder, sampling, max_buffer_size
                    , max_num_seen_examples, load_path, dataset_sequence, adaptation)
                    main_adapt.main()
run_experiments(seeds, sampling_methods, buffer_sizes, sequences, max_num_seen_examples)


buffer_sizes = [-1]
sampling_methods = ['reservoir']
run_experiments(seeds, sampling_methods, buffer_sizes, sequences, max_num_seen_examples)