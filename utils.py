import os
import zipfile
import numpy as np
import torch


def load_metr_la_data():

    # X = np.load("data/node_values_origin.npy")
    # X = X.transpose((1, 2, 0))
    # A = np.load("data/adj_mat_origin.npy")

    A = np.load("data/w_249.npy")
    X = np.load("data/flow_249.npy")
    node_class = np.load("data/node_class.npy", allow_pickle=True)[:, 2]
    # A = np.load("data/nodes_38/w_38.npy")
    # X = np.load("data/nodes_38/flow_38.npy")
    # node_class = np.load("data/nodes_38/node_class.npy", allow_pickle=True)[:, 1]
    nodes = []
    for item in node_class:
        if item == 'FR':
            nodes.append(0)
        if item == 'ML':
            nodes.append(1)
        if item == 'OR':
            nodes.append(2)
    nodes = np.array(nodes)


    X = np.reshape(X, (X.shape[0], X.shape[1], 1)).transpose((1, 2, 0))
    #
    # X_val = np.load("data/V_25_test.npy")
    # X_val = np.reshape(X_val, (X_val.shape[0], X_val.shape[1], 1)).transpose((1, 2, 0))


    A = A.astype(np.float32)
    X = X.astype(np.float32)
    # X_val = X_val.astype(np.float32)

    # Normalization using Z-score method
    means = np.mean(X, axis=(0, 2))
    stds = np.std(X, axis=(0, 2))
    X = X - means.reshape(1, -1, 1)
    # X_val = X_val - means.reshape(1, -1, 1)
    X = X / stds.reshape(1, -1, 1)
    # X_val = X_val / stds.reshape(1, -1, 1)




    # max_weather = np.max(Weather)
    # min_weather = np.min(Weather)
    # Weather = (Weather - max_weather) / (max_weather - min_weather)

    return A, X, means, stds, nodes

    # Normalization using Max-Min method
    # max_X, min_X = np.max(X), np.min(X)
    # _range = max_X - min_X
    # X = (X - min_X) / _range
    # return A, X, max_X, min_X

    # Normalization using Max method
    # max_value = X.max()
    # X = X / max_value
    # X_val = X_val / max_value
    # return A, X, max_value, X_val

def get_normalized_adj(A):
    """
    Returns the degree normalized adjacency matrix.
    """
    A = A + np.diag(np.ones(A.shape[0], dtype=np.float32))
    D = np.array(np.sum(A, axis=1)).reshape((-1,))
    D[D <= 10e-5] = 10e-5    # Prevent infs
    diag = np.reciprocal(np.sqrt(D))
    A_wave = np.multiply(np.multiply(diag.reshape((-1, 1)), A),
                         diag.reshape((1, -1)))
    return A_wave


def generate_dataset(X, num_timesteps_input, num_timesteps_output):
    """
    Takes node features for the graph and divides them into multiple samples
    along the time-axis by sliding a window of size (num_timesteps_input+
    num_timesteps_output) across it in steps of 1.
    :param X: Node features of shape (num_vertices, num_features,
    num_timesteps)
    :return:
        - Node features divided into multiple samples. Shape is
          (num_samples, num_vertices, num_features, num_timesteps_input).
        - Node targets for the samples. Shape is
          (num_samples, num_vertices, num_features, num_timesteps_output).
    """
    # Generate the beginning index and the ending index of a sample, which
    # contains (num_points_for_training + num_points_for_predicting) points
    indices = [(i, i + (num_timesteps_input + num_timesteps_output)) for i
               in range(X.shape[2] - (
                num_timesteps_input + num_timesteps_output) + 1)]

    # Save samples
    features, target = [], []
    for i, j in indices:
        features.append(
            X[:, :, i: i + num_timesteps_input].transpose(
                (0, 2, 1)))
        target.append(X[:, 0, i + num_timesteps_input: j])

    return torch.from_numpy(np.array(features)), \
           torch.from_numpy(np.array(target))


def z_score(x, mean, std):
    '''
    Z-score normalization function: $z = (X - \mu) / \sigma $,
    where z is the z-score, X is the value of the element,
    $\mu$ is the population mean, and $\sigma$ is the standard deviation.
    :param x: np.ndarray, input array to be normalized.
    :param mean: float, the value of meadard deviation.
    :return: np.ndarray, z-score normalin.
    :param std: float, the value of stanzed array.
    '''
    return (x - mean) / std


def z_inverse(x, mean, std):
    '''
    The inverse of function z_score().
    :param x: np.ndarray, input to be recovered.
    :param mean: float, the value of mean.
    :param std: float, the value of standard deviation.
    :return: np.ndarray, z-score inverse array.
    '''
    return x * std + mean


def MAPE(v, v_):
    '''
    Mean absolute percentage error.
    :param v: np.ndarray or int, ground truth.
    :param v_: np.ndarray or int, prediction.
    :return: int, MAPE averages on all elements of input.
    '''
    return np.mean(np.abs(v_ - v) / (v + 1e-5))


def RMSE(v, v_):
    '''
    Mean squared error.
    :param v: np.ndarray or int, ground truth.
    :param v_: np.ndarray or int, prediction.
    :return: int, RMSE averages on all elements of input.
    '''
    return np.sqrt(np.mean((v_ - v) ** 2))


def MAE(v, v_):
    '''
    Mean absolute error.
    :param v: np.ndarray or int, ground truth.
    :param v_: np.ndarray or int, prediction.
    :return: int, MAE averages on all elements of input.
    '''
    return np.mean(np.abs(v_ - v))


def CalConfusionMatrix(confusion_matrix):
    TP, FP, FN, TN, precise, recall, f1_score = 0, 0, 0, 0, 0, 0, 0
    n = confusion_matrix.shape[0]
    # fpr, tpr = [], []
    for i in range(n):
        TP = confusion_matrix[i][i]
        FP = (confusion_matrix[i].sum() - TP)
        FN = (confusion_matrix[:, i].sum() - TP)
        TN = (confusion_matrix.sum() - TP - FP - FN)
        if TP != 0:
            precise_temp = Precise(TP, FP)
            precise += precise_temp
            recall_temp = ReCall(TP, FN)
            recall += recall_temp
            f1_score += F1_Score(precise_temp, recall_temp)
            # fpr += FPR(FP, TN)
            # tpr += ReCall(TP, FN)
            # fpr.append(FPR(FP, TN))
            # tpr.append(ReCall(TP, FN))
        else:
            precise += 0.
            recall += 0.
            f1_score += 0.
            # fpr.append(0.)
            # tpr.append(0.)
    return precise / n, recall / n, f1_score / n


def Precise(TP, FP):
    return TP / (TP + FP)


def ReCall(TP, FN):
    return TP / (TP + FN)


def FPR(FP, TN):
    return FP / (FP + TN)


def F1_Score(P, R):
    return 2 * P * R / (P + R)


