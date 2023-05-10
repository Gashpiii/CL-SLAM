import main_adapt
sampling = 'reservoir'
buffer_sizes = [100, 250, 500, 1000, 2500, 5000, 10000]
sequences = [9, 10] # note: first sequence is actually c since model is pre-trained on that

def find_line_num(text, path):
    file = open(path, 'r+')
    return [num for num,line in enumerate(file) if text in line][0]

def modify_config(path, log_path, load_weights_folder, sampling, maximize_diversity, max_buffer_size
                  , similarity_threshold, similarity_sampling, load_path, dataset_sequence, adaptation):
    config = open(path, 'r+')
    lines = config.readlines()
    config.seek(0)

    lines[find_line_num('  log_path', path)] = f'  log_path: {log_path}\n'    
    lines[find_line_num('  load_weights_folder', path)] = f'  load_weights_folder: {load_weights_folder}\n'
    lines[find_line_num('  sampling', path)] = f'  sampling: {sampling}\n'
    lines[find_line_num('  maximize_diversity', path)] = f'  maximize_diversity: {maximize_diversity}\n'
    lines[find_line_num('  max_buffer_size', path)] = f'  max_buffer_size: {max_buffer_size}\n'
    lines[find_line_num('  similarity_threshold', path)] = f'  similarity_threshold: {similarity_threshold}\n'
    lines[find_line_num('  similarity_sampling', path)] = f'  similarity_sampling: {similarity_sampling}\n'
    lines[find_line_num('  load_path', path)] = f'  load_path: {load_path}\n'
    lines[find_line_num('  dataset_sequence', path)] = f'  dataset_sequence: {dataset_sequence}\n'
    lines[find_line_num('  adaptation', path)] = f'  adaptation: {adaptation}\n'
    
    config.writelines(lines)
    config.truncate()
    config.close()

def run_experiments(sampling, buffer_sizes, sequences):
    for buffer_size in buffer_sizes:
        path = './config/config_adapt.yaml'
        log_path = f'./log/slam/{sampling}_{buffer_size}_c_k{sequences[0]}'
        load_weights_folder = './log/cityscapes/models/weights_025/'
        sampling = sampling
        maximize_diversity = 'False'
        max_buffer_size = buffer_size
        similarity_threshold = 1
        similarity_sampling = 'False'
        load_path = f'./log/cityscapes/replay_buffer_{sampling}_{buffer_size}'
        dataset_sequence = sequences[0]
        adaptation = 'True'

        modify_config(path, log_path, load_weights_folder, sampling, maximize_diversity, max_buffer_size
                , similarity_threshold, similarity_sampling, load_path, dataset_sequence, adaptation)
        main_adapt.main()
        for sequence in sequences[1:]:
            load_weights_folder = f'{log_path}/models/weights_000'
            load_path = f'{log_path}/replay_buffer'
            log_path = f'{log_path}_k{sequence}'
            dataset_sequence = sequence

            modify_config(path, log_path, load_weights_folder, sampling, maximize_diversity, max_buffer_size
                    , similarity_threshold, similarity_sampling, load_path, dataset_sequence, adaptation)
            main_adapt.main()
run_experiments(sampling, buffer_sizes, sequences)

# main_adapt.main()