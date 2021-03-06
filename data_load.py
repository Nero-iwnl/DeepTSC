# encoding utf-8
'''
@Author: william
@Description:
@time:2020/6/15 10:52
'''
from utils import generate_dataset, load_metr_la_data


def Data_load(num_timesteps_input, num_timesteps_output):
    A, X, means, stds, nodes = load_metr_la_data()
    # A, X, max_X, min_X = load_metr_la_data()
    # A, X, max_value, X_val = load_metr_la_data()

    split_line1 = int(X.shape[2] * 0.6)
    split_line2 = int(X.shape[2] * 0.8)

    train_original_data = X[:, :, :split_line1]
    val_original_data = X[:, :, split_line1:split_line2]
    # val_original_data = X_val
    test_original_data = X[:, :, split_line2:]


    training_input, training_target = generate_dataset(train_original_data,
                                                       num_timesteps_input=num_timesteps_input,
                                                       num_timesteps_output=num_timesteps_output)
    val_input, val_target = generate_dataset(val_original_data,
                                             num_timesteps_input=num_timesteps_input,
                                             num_timesteps_output=num_timesteps_output)
    test_input, test_target = generate_dataset(test_original_data,
                                               num_timesteps_input=num_timesteps_input,
                                               num_timesteps_output=num_timesteps_output)

    return A, means, stds, training_input, training_target, val_input, val_target, test_input, test_target, nodes
    # return A, max_X, min_X, training_input, training_target, val_input, val_target, test_input, test_target
    # return A, max_value, training_input, training_target, val_input, val_target, test_input, test_target
