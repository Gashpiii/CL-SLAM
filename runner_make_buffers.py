import make_cityscapes_buffer
import make_cityscapes_mostrecent_buffer

# buffer_sizes = [100, 250, 500, 1000, 2500, 5000, 10000]
# buffer_sizes = [100]
buffer_sizes = [250, 500, 1000, 2500, 5000, 10000]

# # buffer_sizes = [5000]


sampling = 'most-recent'
# # sampling = 'reservoir'

# if sampling == 'most-recent':
#     for buffer_size in buffer_sizes:
#         make_cityscapes_mostrecent_buffer.main(sampling=sampling, max_buffer_size=buffer_size)
# else:
#     for buffer_size in buffer_sizes:
#         make_cityscapes_buffer.main(sampling=sampling, max_buffer_size=buffer_size)
for buffer_size in buffer_sizes:
        make_cityscapes_buffer.main(sampling=sampling, max_buffer_size=buffer_size)
########################################################

# sampling = 'most-recent'
# buffer_size = 100

# make_cityscapes_buffer.main(sampling=sampling, max_buffer_size=buffer_size)
    