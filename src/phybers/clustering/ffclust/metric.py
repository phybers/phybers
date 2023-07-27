import math
import operator
import numpy as np
from random import randint
from dipy.tracking.streamline import length as streamline_length


def recalc_centroid(indices, refdata):
    fibers = {}
    for i in indices:
        f = refdata[i]
        f_lenght = streamline_length(f)
        fibers[i] = f_lenght
    sorted_items = sorted(fibers.items(), key=operator.itemgetter(1))
    sorted_fibers = []
    for item in sorted_items:
        sorted_fibers.append(item[0])
    index_60length = math.ceil(len(sorted_fibers)*0.6) - 1
    index_80length = math.ceil(len(sorted_fibers)*0.8) - 1
    longest_fibers = []
    while index_60length <= index_80length:
        longest_fibers.append(sorted_fibers[index_60length])
        index_60length+=1
    number_fibers_10percent = math.ceil(len(longest_fibers)*0.1)
    fibers_10percent = []
    for i in range(number_fibers_10percent):
        rand_index = randint(1, number_fibers_10percent)
        fibers_10percent.append(longest_fibers[rand_index])

    fibers_data = []
    for index in fibers_10percent:
        fiber = refdata[index]
        fibers_data.append(fiber)
    matrix = matrix_dist(streamlines = np.asarray(fibers_data))

    assert matrix is not None

    min_sum = 0
    for i in range(len(matrix)):
        sum = 0
        for j in range(len(matrix[0])):
            sum += matrix[i][j]
        if (sum < min_sum):
            min_sum = sum

    centroid = fibers_data[len(matrix) - 1]
    return centroid

def matrix_dist(streamlines, get_max=True, get_mean=False):
    """
    Compute distance between all streamlines, can return both max/min distance matrices.
    """
    x = streamlines
    # Output of this computation is a (num_streamlines, num_streamlines, num_points) array.
    # First stack both direct and reversed in an array -> (2, num_streamlines, num_points, dim)
    # using [:,None] create new axis to broadcast computation and perform difference between
    # every pair of streamlines(both direct and reverse), then perform x^2 + y^2 + z^2.
    distances = np.sum(np.square(np.stack((x,x[:,::-1]))[:,None]-x[:,None]), axis=4)

    if get_max and get_mean:
        max_distances = np.sqrt(distances.max(axis=3).min(axis=0))
        mean_distances = np.sqrt(distances.mean(axis=3).min(axis=0))
        return max_distances, mean_distances
    elif get_max:
        return np.sqrt(distances.max(axis=3).min(axis=0))
    elif get_mean:
        return  np.sqrt(distances.mean(axis=3).min(axis=0))
    else:
        print('error, should return atleast one matrix')
